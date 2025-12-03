"""
Task management API endpoints.
Handles creating, retrieving, and managing planning tasks.
"""

import uuid
from datetime import datetime
from typing import List

from app.agents import AgentOrchestrator
from app.core.logging import app_logger
from app.db import get_db
from app.models import AgentLog, Task, TaskStatus
from app.schemas import TaskCreateRequest, TaskModifyRequest, TaskResponse
from app.schemas import TaskStatus as TaskStatusSchema
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/create", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: str = "default_user",  # TODO: Get from auth
):
    """
    Create a new planning task and start agent processing.
    
    Args:
        request: Task creation request
        background_tasks: FastAPI background tasks
        db: Database session
        user_id: User identifier
        
    Returns:
        Created task information
    """
    try:
        # Create task in database
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            user_id=user_id,
            title=request.title,
            description=request.description,
            task_type=request.task_type.value,
            status=TaskStatus.PENDING,
            llm_provider=request.llm_provider.value,
            model_name=request.model_name or "",
            use_custom_rag=1 if request.use_custom_rag else 0,  # Convert bool to int for database
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Start agent processing in background
        background_tasks.add_task(
            process_task_with_agents,
            task_id=task_id,
            task_input={
                "title": request.title,
                "description": request.description,
                "task_type": request.task_type.value,
                "user_id": user_id,
                "use_custom_rag": request.use_custom_rag,
            },
            llm_provider=request.llm_provider.value,
            model_name=request.model_name,
        )
        
        app_logger.info(f"Task created: {task_id}")
        return TaskResponse.model_validate(task)
    
    except Exception as e:
        app_logger.error(f"Error creating task: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    user_id: str = "default_user",
):
    """
    Get task information by ID.
    
    Args:
        task_id: Task identifier
        db: Database session
        user_id: User identifier
        
    Returns:
        Task information
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse.model_validate(task)


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    user_id: str = "default_user",
):
    """
    List all tasks for a user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        user_id: User identifier
        
    Returns:
        List of tasks
    """
    tasks = db.query(Task).filter(
        Task.user_id == user_id
    ).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    return [TaskResponse.model_validate(task) for task in tasks]


@router.post("/{task_id}/modify", response_model=TaskResponse)
async def modify_task(
    task_id: str,
    request: TaskModifyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: str = "default_user",
):
    """
    Modify an existing task/plan based on user feedback.
    
    Args:
        task_id: Task identifier
        request: Modification request
        background_tasks: FastAPI background tasks
        db: Database session
        user_id: User identifier
        
    Returns:
        Updated task information
    """
    # Get task
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Can only modify completed tasks"
        )
    
    # Update task status
    task.status = TaskStatus.REVIEWING
    db.commit()
    
    # Use LLM settings from request if provided, otherwise use task's original settings
    llm_provider = request.llm_provider or task.llm_provider
    model_name = request.model_name or task.model_name
    use_custom_rag = request.use_custom_rag if request.use_custom_rag is not None else getattr(task, 'use_custom_rag', False)
    
    # Start modification in background
    background_tasks.add_task(
        modify_task_with_agents,
        task_id=task_id,
        modification_request=request.modification_request,
        llm_provider=llm_provider,
        model_name=model_name,
        use_custom_rag=use_custom_rag,
    )
    
    db.refresh(task)
    return TaskResponse.model_validate(task)


async def process_task_with_agents(
    task_id: str,
    task_input: dict,
    llm_provider: str,
    model_name: str = None,
):
    """
    Background task to process task with agent orchestrator.
    
    Args:
        task_id: Task identifier
        task_input: Task input data
        llm_provider: LLM provider to use
        model_name: Model name
    """
    from app.db import SessionLocal
    
    db = SessionLocal()
    try:
        # Update status to processing
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        
        task.status = TaskStatus.PROCESSING
        db.commit()
        
        # Get use_custom_rag from task_input
        use_custom_rag = task_input.get("use_custom_rag", False)
        
        # Create orchestrator and execute workflow
        orchestrator = AgentOrchestrator(
            llm_provider=llm_provider,
            model_name=model_name,
            use_custom_rag=use_custom_rag,
        )
        
        result = await orchestrator.execute_full_workflow(task_input)
        
        # Update task with results
        task.research_output = result.get("research")
        task.plan_output = result.get("plan")
        task.review_output = result.get("review")
        task.final_output = result
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        
        db.commit()
        app_logger.info(f"Task completed: {task_id}")
    
    except Exception as e:
        app_logger.error(f"Error processing task {task_id}: {e}")
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.FAILED
            db.commit()
    
    finally:
        db.close()


async def modify_task_with_agents(
    task_id: str,
    modification_request: str,
    llm_provider: str,
    model_name: str = None,
    use_custom_rag: bool = False,
):
    """
    Background task to modify task with agents.
    
    Args:
        task_id: Task identifier
        modification_request: User's modification request
        llm_provider: LLM provider
        model_name: Model name
        use_custom_rag: Force use of custom RAG data only
    """
    from app.db import SessionLocal
    
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        
        # Create orchestrator
        orchestrator = AgentOrchestrator(
            llm_provider=llm_provider,
            model_name=model_name,
            use_custom_rag=use_custom_rag,
        )
        
        # Modify plan
        original_output = task.final_output or {}
        task_context = {
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "user_id": task.user_id,
        }
        
        modified_output = await orchestrator.modify_plan(
            original_output=original_output,
            modification_request=modification_request,
            task_context=task_context,
        )
        
        # Update task - the modified output should go to review_output since that's what's displayed
        task.final_output = modified_output
        task.review_output = modified_output.get("plan")  # Update review_output instead of plan_output
        task.status = TaskStatus.COMPLETED
        task.updated_at = datetime.utcnow()
        
        db.commit()
        app_logger.info(f"Task modified: {task_id}")
    
    except Exception as e:
        app_logger.error(f"Error modifying task {task_id}: {e}")
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.FAILED
            db.commit()
    
    finally:
        db.close()


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    user_id: str = "default_user",
):
    """
    Delete a task.
    
    Args:
        task_id: Task identifier
        db: Database session
        user_id: User identifier
        
    Returns:
        Success message
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}
