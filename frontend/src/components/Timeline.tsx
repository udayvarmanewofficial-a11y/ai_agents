import React from 'react';

interface TimelineStage {
  id: string;
  name: string;
  icon: string;
  status: 'completed' | 'active' | 'pending' | 'error';
  description?: string;
  duration?: string;
}

interface TimelineProps {
  stages: TimelineStage[];
}

const Timeline: React.FC<TimelineProps> = ({ stages }) => {
  const getStageStyles = (status: string) => {
    switch (status) {
      case 'completed':
        return {
          circle: 'bg-green-500 border-green-600 shadow-lg',
          text: 'text-green-700',
          line: 'bg-green-500',
        };
      case 'active':
        return {
          circle: 'bg-blue-500 border-blue-600 shadow-lg animate-pulse',
          text: 'text-blue-700 font-semibold',
          line: 'bg-gray-300',
        };
      case 'error':
        return {
          circle: 'bg-red-500 border-red-600 shadow-lg',
          text: 'text-red-700',
          line: 'bg-gray-300',
        };
      default:
        return {
          circle: 'bg-gray-300 border-gray-400',
          text: 'text-gray-500',
          line: 'bg-gray-300',
        };
    }
  };

  return (
    <div className="py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Mobile View - Vertical Timeline */}
        <div className="md:hidden space-y-6">
          {stages.map((stage, index) => {
            const styles = getStageStyles(stage.status);
            return (
              <div key={stage.id} className="flex items-start space-x-4">
                {/* Circle and Line */}
                <div className="flex flex-col items-center">
                  <div 
                    className={`w-12 h-12 rounded-full border-4 flex items-center justify-center text-xl ${styles.circle} transition-all duration-300`}
                  >
                    {stage.icon}
                  </div>
                  {index < stages.length - 1 && (
                    <div className={`w-1 h-16 mt-2 ${styles.line} transition-all duration-500`} />
                  )}
                </div>
                
                {/* Content */}
                <div className="flex-1 pt-2">
                  <p className={`text-sm font-semibold ${styles.text}`}>
                    {stage.name}
                  </p>
                  {stage.description && (
                    <p className="text-xs text-gray-600 mt-1">{stage.description}</p>
                  )}
                  {stage.status === 'active' && (
                    <p className="text-xs text-blue-600 mt-1 animate-pulse">
                      In progress...
                    </p>
                  )}
                  {stage.status === 'completed' && stage.duration && (
                    <p className="text-xs text-gray-500 mt-1">
                      ✓ Completed in {stage.duration}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Desktop View - Horizontal Timeline */}
        <div className="hidden md:block">
          <div className="flex items-center justify-between relative">
            {/* Background Line */}
            <div className="absolute top-8 left-0 right-0 h-1 bg-gray-200 -z-10" />
            
            {stages.map((stage, index) => {
              const styles = getStageStyles(stage.status);
              const prevCompleted = index === 0 || stages[index - 1].status === 'completed';
              
              return (
                <React.Fragment key={stage.id}>
                  <div className="flex flex-col items-center flex-1 relative">
                    {/* Stage Circle */}
                    <div 
                      className={`w-16 h-16 rounded-full border-4 flex items-center justify-center text-2xl ${styles.circle} transition-all duration-300 bg-white z-10`}
                    >
                      {stage.icon}
                    </div>
                    
                    {/* Stage Name */}
                    <div className="mt-3 text-center">
                      <p className={`text-sm font-semibold ${styles.text}`}>
                        {stage.name}
                      </p>
                      {stage.description && (
                        <p className="text-xs text-gray-500 mt-1 max-w-[120px]">
                          {stage.description}
                        </p>
                      )}
                      {stage.status === 'active' && (
                        <p className="text-xs text-blue-600 mt-1 animate-pulse">
                          In progress...
                        </p>
                      )}
                      {stage.status === 'completed' && stage.duration && (
                        <p className="text-xs text-gray-500 mt-1">
                          {stage.duration}
                        </p>
                      )}
                      {stage.status === 'error' && (
                        <p className="text-xs text-red-600 mt-1">
                          Failed
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {/* Connecting Line (not after last stage) */}
                  {index < stages.length - 1 && (
                    <div 
                      className={`flex-1 h-1 -mx-8 transition-all duration-500 ${prevCompleted ? styles.line : 'bg-gray-200'}`}
                      style={{ marginTop: '-2rem' }}
                    />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Timeline;
