import React from 'react';

const ThinkingLoader = () => {
  return (
    <div className="flex items-start gap-3 self-start">
      <div className="max-w-xs md:max-w-md p-3 rounded-xl bg-blue-800 text-white relative overflow-hidden shadow-lg">
        <div className="flex items-center justify-between mb-1">
          <span className="font-semibold text-sm">Co-Founder</span>
        </div>

        <div className="flex items-center gap-1 h-6">
          <span
            className="w-3 h-3 bg-white rounded-full animate-bounce"
            style={{ animationDelay: "0s" }}
          ></span>
          <span
            className="w-3 h-3 bg-white rounded-full animate-bounce"
            style={{ animationDelay: "0.3s" }}
          ></span>
          <span
            className="w-3 h-3 bg-white rounded-full animate-bounce"
            style={{ animationDelay: "0.45s" }}
          ></span>
          <span
            className="w-3 h-3 bg-white rounded-full animate-bounce"
            style={{ animationDelay: "0.6s" }}
          ></span>
          <span
            className="w-3 h-3 bg-white rounded-full animate-bounce"
            style={{ animationDelay: "0.75s" }}
          ></span>
        </div>

        <p className="text-sm text-white mt-2 opacity-70 font-roboto">Co-Founder is thinking...</p>
      </div>
    </div>
  );
};

export default ThinkingLoader;