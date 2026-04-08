import React, { useState, useRef, useEffect } from "react";
import { researchApi } from "../config/congfiguration";

const ResearchBox: React.FC = () => {
   const [query, setQuery] = useState<string>("");
   const [result, setResult] = useState<string>("");


   const [taskId, setTaskId] = useState<string>("");
   const [plan, setPlan] = useState<{ type: string }[]>([]);
   const [currentStep, setCurrentStep] = useState<string>("");

   const [logs, setLogs] = useState<Record<string, string>>({});
   const [completedSteps, setCompletedSteps] = useState<string[]>([]);


   const bottomRef = useRef<HTMLDivElement>(null);
   const logsBottomRef = useRef<HTMLDivElement>(null);

   useEffect(() => {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
   }, [result]);


   useEffect(() => {
      logsBottomRef.current?.scrollIntoView({ behavior: "smooth" });
   }, [logs]);



   const handleResearch = async () => {
      if (!query.trim()) return;

      setResult("");
      setTaskId("");
      setPlan([]);
      setCurrentStep("");

      try {
         const res = await researchApi(query);

         const taskId = res.task_id;
         setTaskId(taskId);
         setPlan(res.plan || []);
         console.log("Received plan:", res.plan);

         const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${taskId}`);

         socket.onopen = () => {
            console.log("-- WebSocket connected --");
         };

         socket.onmessage = (event) => {
            if (event.data === "[DONE]") {
               socket.close();
               return;
            }

            if (event.data === "__ping__") return;

            try {
               const parsed = JSON.parse(event.data);

               if (parsed.type === "step") {
                  setCurrentStep(parsed.step);
                  console.log("Current step:", parsed.step);
                  return;
               }
               if (parsed.type === "log") {
                  console.log(`Log for ${parsed.step}:`, parsed.content);
                  setCurrentStep(parsed.step);
                  setLogs((prev) => ({
                     ...prev,
                     [parsed.step]: (prev[parsed.step] || "") + parsed.content,
                  }));
                  return;
               }
               if (parsed.type === "done") {
                  setCompletedSteps((prev) => [...prev, parsed.step]);
                  return;
               }

            } catch {
               setResult((prev) => prev + event.data);
            }
         };

         socket.onerror = (err) => {
            console.error("WebSocket error:", err);
            setResult("Error in streaming");
         };

         socket.onclose = () => {
            console.log("--- WebSocket closed ---");
         };
      } catch (error) {
         console.error(error);
         setResult("API Error");
      }
   };

   return (
      <div className="flex h-screen w-full">

         <div className="flex flex-col w-4/5 bg-gray-900 text-white p-4 relative">

            <h2 className="text-xl font-bold text-center mb-2">
               Gas Town Multi-Agent Orchestration System
            </h2>

            {result && (
               <div className="flex-1 bg-gray-800 border border-gray-700 rounded-lg p-4 overflow-y-auto max-h-[87vh] custom-scrollbar">
                  <pre className="whitespace-pre-wrap wrap-break-words text-sm leading-relaxed">
                     {result}
                     <div ref={bottomRef} />
                  </pre>
               </div>
            )}

            {/* INPUT */}
            <div className="flex gap-3 absolute bottom-2 left-0 w-full px-4">
               <input
                  className="flex-1 bg-gray-800 border border-gray-600 text-white px-4 py-2 rounded-lg focus:outline-none hover:focus:ring-2 focus:ring-blue-500"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter topic..."
               />

               <button
                  onClick={handleResearch}
                  className=" px-5 py-2 rounded-lg font-semibold border border-gray-600 focus:outline-none hover:focus:ring-2 focus:ring-blue-500"
               >
                  Send
               </button>
            </div>
         </div>

         <div className="w-1/5 bg-gray-950 text-white p-4 border-l border-gray-700 relative ">

            <h3 className="text-lg font-bold mb-4">Mayor Plan & Actions</h3>

            <div className="space-y-3 overflow-y-auto custom-scrollbar max-h-[75vh]">
               <div>{taskId}</div>
               {plan.map((p, i) => {
                  const isActive = currentStep === p.type;
                  const isDone = completedSteps.includes(p.type);

                  return (
                     <div key={i} className="rounded-lg bg-gray-800 p-2 ">

                        {/* STEP HEADER */}
                        <div
                           className={`flex justify-between items-center ${isActive ? "text-green-400 font-bold" : ""
                              }`}
                        >

                           <span className="flex items-center gap-2">
                              {isDone ? (
                                 "✔"
                              ) : isActive ? (
                                 <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                              ) : (
                                 "⬜"
                              )}

                              {p.type.toUpperCase()}
                           </span>
                        </div>

                        {/* LOGS */}

                        {logs[p.type] && (
                           <div className="mt-2 bg-gray-700 p-2 rounded-lg max-h-20 overflow-y-auto custom-scrollbar overflow-x-hidden">
                              <pre className="whitespace-pre-wrap wrap-break-words mt-2 text-xs text-gray-300">
                                 {logs[p.type]}
                                 <div ref={logsBottomRef} />
                              </pre>
                           </div>
                        )}
                     </div>
                  );

               })}
            </div>

            {currentStep && (
               <div className="mt-6 border-t-2 ">
                  <h4 className="text-md font-semibold mt-2">Current Running Agent</h4>
                  <div className="bg-blue-600 p-2 rounded-lg text-center">
                     {currentStep.toUpperCase()}
                  </div>
               </div>
            )}

            {plan.length > 0 && (
               <div className="mt-2 ">
                  <h4 className="text-sm mb-2">Progress</h4>

                  {(() => {
                     const currentIndex = plan.findIndex(
                        (p) =>
                           p.type.toLowerCase() === currentStep.toLowerCase()
                     );

                     const progress =
                        currentIndex >= 0
                           ? ((currentIndex + 1) / plan.length) * 100
                           : 0;

                     return (
                        <div className="bg-white h-2 rounded">
                           <div
                              className="bg-green-500 h-2 rounded transition-all duration-500"
                              style={{ width: `${progress}%` }}
                           />
                           {Math.round(progress)}%
                        </div>
                     );
                  })()}
               </div>
            )}

         </div>

      </div>
   );
};

export default ResearchBox;