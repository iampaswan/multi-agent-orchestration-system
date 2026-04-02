import React, { useState, useRef, useEffect } from "react";
import { researchApi } from "../config/congfiguration";


const ResearchBox: React.FC = () => {
   const [query, setQuery] = useState<string>("");
   const [result, setResult] = useState<string>("");

   const bottomRef = useRef<HTMLDivElement>(null);

   useEffect(() => {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
   }, [result]);

   const handleResearch = async () => {
      if (!query.trim()) return;

      setResult("");

      try {
         // Step 1: start research
         const res = await researchApi(query);
         const taskId = res.task_id;

         // Step 2: open websocket
         const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${taskId}`);

         socket.onopen = () => {
            console.log("-- WebSocket connected --");
         };

         socket.onmessage = (event) => {
            if (event.data === "[DONE]") {
               socket.close();
               return;
            }

            setResult((prev) => prev + event.data);
         };

         socket.onmessage = (event) => {
            if (event.data === "__ping__") return;
            console.log(event.data);
         };

         socket.onerror = (err) => {
            console.error("WebSocket error:", err);
            setResult(" Error in streaming");
         };

         socket.onclose = () => {
            console.log("WebSocket closed");
         };

      } catch (error) {
         console.error(error);
         setResult(" API Error");
      }
   };



   return (


      <div className="flex flex-col gap-2 h-screen w-full bg-gray-900 text-white p-4 overflow-hidden postion-relative">

         <h2 className="text-xl font-bold text-center">
            Gas Town Multi-Agent Orchestration System
         </h2>



         {result && (
            <div className="flex-1 bg-gray-800 border border-gray-700 rounded-lg p-4 overflow-y-auto custom-scrollbar max-h-[88vh]">
               <pre className="whitespace-pre-wrap wrap-break-words text-sm leading-relaxed">
                  {result}
               </pre>
               <div ref={bottomRef} />
            </div>
         )}

         <div className="flex gap-3 m-b-4 absolute bottom-0 left-0 w-full mb-2 px-4">

            <input
               className="flex-1 bg-gray-800 border border-gray-600 text-white placeholder-gray-400 px-4 py-2 rounded-lg 
               focus:outline-none hover:border-blue-500 focus:ring-2 focus:ring-blue-500"
               type="text"
               value={query}
               onChange={(e) => setQuery(e.target.value)}
               placeholder="Enter topic..."
            />

            <button
               onClick={handleResearch}
               className="bg-blue-600 hover:border-blue-600 hover:focus:ring-2 focus:ring-blue-500 transition px-5 py-2 
               border border-gray-600 rounded-lg font-semibold p-2"
            >
               Send
            </button>

         </div>

      </div>
   );
};

export default ResearchBox;