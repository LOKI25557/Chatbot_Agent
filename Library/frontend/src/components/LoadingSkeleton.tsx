import React from 'react';

export const LoadingSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div
          key={i}
          className="rounded-2xl border border-library-border dark:border-library-darkBorder bg-white dark:bg-library-darkCard p-5 space-y-4 shadow-sm"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-14 h-20 rounded-lg skeleton-shimmer bg-slate-200 dark:bg-slate-800" />
              <div className="space-y-2">
                <div className="w-20 h-4 rounded-full skeleton-shimmer bg-slate-200 dark:bg-slate-800" />
                <div className="w-16 h-3 rounded-full skeleton-shimmer bg-slate-200 dark:bg-slate-800" />
              </div>
            </div>
            <div className="w-24 h-5 rounded-full skeleton-shimmer bg-slate-200 dark:bg-slate-800" />
          </div>

          <div className="space-y-2">
            <div className="w-3/4 h-5 rounded skeleton-shimmer bg-slate-200 dark:bg-slate-800" />
            <div className="w-1/2 h-4 rounded skeleton-shimmer bg-slate-200 dark:bg-slate-800" />
          </div>

          <div className="space-y-1.5 pt-2">
            <div className="w-full h-3 rounded skeleton-shimmer bg-slate-200 dark:bg-slate-800" />
            <div className="w-4/5 h-3 rounded skeleton-shimmer bg-slate-200 dark:bg-slate-800" />
          </div>

          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-between">
            <div className="w-28 h-4 rounded skeleton-shimmer bg-slate-200 dark:bg-slate-800" />
            <div className="w-16 h-4 rounded skeleton-shimmer bg-slate-200 dark:bg-slate-800" />
          </div>
        </div>
      ))}
    </div>
  );
};
