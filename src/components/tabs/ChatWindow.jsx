import { Send, X, Download, AlertTriangle, Gauge, RotateCcw, ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useReducer, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { toast } from "react-toastify";
import { chatService } from "../../services/chatService";
import EntrepreneurialResponse from "../../components/EntrepreneurialResponse";
import ThinkingLoader from "../ThinkingLoader";

const DRAFT_KEY = "chat_draft";

const initialState = {
  chats: [],
  messages: [],
  status: "idle",
  error: null,
  currentChatId: null,
};

function reducer(state, action) {
  switch (action.type) {
    case "LOAD":
      return { ...state, messages: action.payload.messages || [] };
    case "ADD_MESSAGE":
      return { ...state, messages: [...state.messages, action.payload] };
    case "SET_STATUS":
      return { ...state, status: action.payload };
    case "SET_ERROR":
      return { ...state, error: action.payload, status: action.payload ? "error" : "idle" };
    case "SET_CURRENT_CHAT":
      return { ...state, currentChatId: action.payload };
    case "ADD_CHAT":
      return { ...state, chats: [action.payload, ...state.chats] };
    case "LOAD_CHATS":
      return { ...state, chats: action.payload };
    case "RESET_MESSAGES":
      return { ...state, messages: [], currentChatId: null };
    case "MARK_MESSAGE_FAILED":
      return {
        ...state,
        messages: state.messages.map((m) =>
          m.id === action.payload.id ? { ...m, failed: true } : m
        ),
      };
    case "CLEAR_MESSAGE_FAILED":
      return {
        ...state,
        messages: state.messages.map((m) =>
          m.id === action.payload.id ? { ...m, failed: false } : m
        ),
      };
    default:
      return state;
  }
};

export const ChatWindow = ({ activeTab }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [draft, setDraft] = useState("");
  const [uploadingFile, setUploadingFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const [tokenStats, setTokenStats] = useState({ total: null, used: null });
  const [activeStep, setActiveStep] = useState(1);
  const [isStepsSidebarOpen, setIsStepsSidebarOpen] = useState(false);
  const [isSendDisabled, setIsSendDisabled] = useState(false);

  const steps = [
    { number: 1, title: "Foundation and Preparation" },
    { number: 2, title: "Market Research and Validation" },
    { number: 3, title: "Business and Legal Foundation" },
    { number: 4, title: "Minimum Viable Product (MVP)" },
    { number: 5, title: "Systems and Infrastructure" },
    { number: 6, title: "Launch and Early Operations" },
    { number: 7, title: "Scaling Operations" },
  ];

  const isCoFounder = activeTab === "ai-co-founder";

  // Helper function to clean error messages (remove status codes and technical details)
  const cleanErrorMessage = (error) => {
    if (!error) return "An error occurred. Please try again.";
    
    let message = typeof error === 'string' ? error : error.message || String(error);
    
    // Remove HTTP status codes (e.g., "404", "500", "401", etc.)
    message = message.replace(/\b\d{3}\b/g, '');
    
    // Remove common technical error prefixes
    message = message.replace(/^(Error|Failed|Network|Request|Response):\s*/i, '');
    
    // Remove status code patterns like "Status: 404" or "(404)"
    message = message.replace(/\(?\d{3}\)?/g, '');
    message = message.replace(/Status:\s*\d+/gi, '');
    
    // Clean up extra spaces
    message = message.replace(/\s+/g, ' ').trim();
    
    // If message is empty after cleaning, provide a default
    if (!message) {
      return "Something went wrong. Please try again.";
    }
    
    return message;
  };

  const loadAllChats = async () => {
    try {
      const chats = await chatService.getAllChats();
      dispatch({ type: "LOAD_CHATS", payload: chats });
      return chats;
    } catch (err) {
      console.error('Failed to load chats:', err);
      return [];
    }
  };

  useEffect(() => {
    const saved = localStorage.getItem(DRAFT_KEY);
    if (saved) setDraft(saved);

    if (isCoFounder) {
      (async () => {
        try {
          const stats = await chatService.getTokenStats();
          setTokenStats(stats);
        } catch (e) {
        }
        const chats = await loadAllChats();
        if (chats && chats.length > 0) {
          const mostRecentChat = chats[chats.length - 1]; // here we will change the chat length
          await loadChatHistory(mostRecentChat.id);
        }
      })();
    }
  }, [isCoFounder]);

  // Watch for token exhaustion and show toast
  useEffect(() => {
    if (isCoFounder && tokenStats.total && tokenStats.used !== null) {
      const totalLimit = typeof tokenStats.total === 'number' ? tokenStats.total : 20000;
      const usedValue = typeof tokenStats.used === 'number' ? tokenStats.used : 0;
      const exhausted = usedValue >= totalLimit && totalLimit > 0;
      
      if (exhausted) {
        toast.error("Token consumed, add more tokens to continue.", {
          position: "top-right",
          autoClose: 5000,
        });
      }
    }
  }, [tokenStats, isCoFounder]);

  useEffect(() => {
    localStorage.setItem(DRAFT_KEY, draft);
  }, [draft]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [state.messages]);

  const handleNewChat = async () => {
    try {
      dispatch({ type: "SET_STATUS", payload: "creating" });

      // Clear everything first to show empty state immediately
      dispatch({ type: "RESET_MESSAGES" });
      setDraft(""); // Clear the input draft
      setActiveStep(1); // Reset to Step 1
      dispatch({ type: "SET_ERROR", payload: null }); // Clear any previous errors
      setIsSendDisabled(false); // Reset send button disabled state

      // Create new chat
      const { chatId } = await chatService.createNewChat();
      dispatch({ type: "SET_CURRENT_CHAT", payload: chatId });

      dispatch({ type: "SET_STATUS", payload: "idle" });
    } catch (err) {
      console.error('Failed to create new chat:', err);
      dispatch({ type: "SET_STATUS", payload: "idle" });
      const errorMessage = cleanErrorMessage(err);
      toast.error(errorMessage || "Failed to create new chat. Please try again.", {
        position: "top-right",
        autoClose: 5000,
      });
      dispatch({
        type: "SET_ERROR",
        payload: "Failed to create new chat. Please try again.",
      });
    }
  };

  const loadChatHistory = async (chatId) => {
    try {
      dispatch({ type: "SET_STATUS", payload: "loading" });
      const messages = await chatService.getChatMessages(chatId);
      dispatch({ type: "LOAD", payload: { messages } });
      dispatch({ type: "SET_CURRENT_CHAT", payload: chatId });
      dispatch({ type: "SET_STATUS", payload: "idle" });
    } catch (err) {
      console.error('Failed to load chat history:', err);
      dispatch({ type: "SET_STATUS", payload: "idle" });
      const errorMessage = cleanErrorMessage(err);
      toast.error(errorMessage || "Failed to load chat history. Please try again.", {
        position: "top-right",
        autoClose: 5000,
      });
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!draft.trim() && !uploadingFile) return;

    let chatId = state.currentChatId;

    if (!chatId) {
      try {
        const { chatId: newChatId } = await chatService.createNewChat();
        chatId = newChatId;
        dispatch({ type: "SET_CURRENT_CHAT", payload: chatId });
        await loadAllChats();
      } catch (err) {
        const errorMessage = cleanErrorMessage(err);
        toast.error(errorMessage || "Failed to create chat. Please try again.", {
          position: "top-right",
          autoClose: 5000,
        });
        dispatch({
          type: "SET_ERROR",
          payload: "Failed to create chat. Please try again.",
        });
        return;
      }
    }

    const content = draft.trim() || uploadingFile?.name;

    const userTimestamp = new Date().toLocaleString("en-US", {
      hour: "numeric",
      minute: "numeric",
      hour12: true,
      month: "short",
      day: "numeric",
    });

    const userMsg = {
      id: Date.now().toString(),
      sender: "user",
      text: content,
      timestamp: userTimestamp,
      file: uploadingFile || null,
    };

    dispatch({ type: "ADD_MESSAGE", payload: userMsg });
    setDraft("");
    setUploadingFile(null);
    setUploadProgress(0);
    dispatch({ type: "SET_STATUS", payload: "sending" });

    // Format step as "entrepreneur_step_{activeStep}"
    const step = `entrepreneur_step_${activeStep}`;

    try {
      const response = await chatService.sendMessage(chatId, content, step);

      const aiTimestamp = new Date().toLocaleString("en-US", {
        hour: "numeric",
        minute: "numeric",
        hour12: true,
        month: "short",
        day: "numeric",
      });

      // Extract text content from response.data, handling both string and object cases
      let textContent = '';
      if (response.type === 'general_response') {
        if (typeof response.data === 'string') {
          textContent = response.data;
        } else if (response.data && typeof response.data === 'object') {
          // If data is an object, check for text/message property (markdown), otherwise stringify
          textContent = response.data.text || response.data.message || JSON.stringify(response.data, null, 2);
        } else {
          textContent = String(response.data ?? '');
        }
      }

      const aiMsg = {
        id: `${Date.now()}-ai`,
        sender: "ai",
        text: textContent,
        type: response.type,
        payload: response,
        timestamp: aiTimestamp,
      };

      dispatch({ type: "ADD_MESSAGE", payload: aiMsg });
      dispatch({ type: "SET_STATUS", payload: "idle" });

      try {
        const stats = await chatService.getTokenStats();
        setTokenStats(stats);
      } catch { }
    } catch (err) {
      dispatch({ type: "MARK_MESSAGE_FAILED", payload: { id: userMsg.id } });
      
      // Handle 402 error: disable send button and show notification message
      if (err.status === 402 && err.responseData) {
        setIsSendDisabled(true);
        const notificationMessage = err.responseData.notifiy || err.responseData.notify || "Token consumed, please buy the tokens";
        toast.error(notificationMessage, {
          position: "top-right",
          autoClose: 5000,
        });
        dispatch({
          type: "SET_ERROR",
          payload: notificationMessage,
        });
        dispatch({ type: "SET_STATUS", payload: "idle" });
        return;
      }
      
      const errorMessage = cleanErrorMessage(err);
      toast.error(errorMessage || "Failed to send message. Please try again.", {
        position: "top-right",
        autoClose: 5000,
      });
      dispatch({
        type: "SET_ERROR",
        payload: err.message || "Failed to send message",
      });
      dispatch({ type: "SET_STATUS", payload: "idle" });
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadingFile(file);
      setUploadProgress(0);

      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 5;
        });
      }, 100);
    }
  };

  const handleImageDownload = async (imageUrl) => {
    try {
      // Fetch the image
      const response = await fetch(imageUrl);
      const blob = await response.blob();

      // Create a temporary URL for the blob
      const blobUrl = window.URL.createObjectURL(blob);

      // Create a temporary anchor element
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = `generated-logo-${Date.now()}.png`; // Default filename
      document.body.appendChild(link);

      // Trigger the download
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error('Failed to download image:', error);
      // Fallback to opening in new tab if download fails
      window.open(imageUrl, '_blank', 'noopener,noreferrer');
    }
  };

  const handleRetrySend = async (failedMsg) => {
    if (!failedMsg || failedMsg.sender !== 'user') return;
    const content = failedMsg.text;
    let chatId = state.currentChatId;
    if (!chatId) return; // should exist since we created it before sending

    dispatch({ type: "SET_STATUS", payload: "sending" });

    // Format step as "entrepreneur_step_{activeStep}"
    const step = `entrepreneur_step_${activeStep}`;

    try {
      const response = await chatService.sendMessage(chatId, content, step);

      // Only clear failed flag if retry is successful
      dispatch({ type: "CLEAR_MESSAGE_FAILED", payload: { id: failedMsg.id } });

      const aiTimestamp = new Date().toLocaleString("en-US", {
        hour: "numeric",
        minute: "numeric",
        hour12: true,
        month: "short",
        day: "numeric",
      });
      // Extract text content from response.data, handling both string and object cases
      let textContent = '';
      if (response.type === 'general_response') {
        if (typeof response.data === 'string') {
          textContent = response.data;
        } else if (response.data && typeof response.data === 'object') {
          // If data is an object, check for text/message property (markdown), otherwise stringify
          textContent = response.data.text || response.data.message || JSON.stringify(response.data, null, 2);
        } else {
          textContent = String(response.data ?? '');
        }
      }

      const aiMsg = {
        id: `${Date.now()}-ai`,
        sender: "ai",
        text: textContent,
        type: response.type,
        payload: response,
        timestamp: aiTimestamp,
      };
      dispatch({ type: "ADD_MESSAGE", payload: aiMsg });
      dispatch({ type: "SET_STATUS", payload: "idle" });

      try {
        const stats = await chatService.getTokenStats();
        setTokenStats(stats);
      } catch { }
    } catch (err) {
      // Re-mark as failed if retry fails, so the button remains visible
      dispatch({ type: "MARK_MESSAGE_FAILED", payload: { id: failedMsg.id } });
      dispatch({ type: "SET_STATUS", payload: "idle" });
      
      // Handle 402 error: disable send button and show notification message
      if (err.status === 402 && err.responseData) {
        setIsSendDisabled(true);
        const notificationMessage = err.responseData.notifiy || err.responseData.notify || "Token consumed, please buy the tokens";
        toast.error(notificationMessage, {
          position: "top-right",
          autoClose: 5000,
        });
        dispatch({
          type: "SET_ERROR",
          payload: notificationMessage,
        });
        return;
      }
      
      const errorMessage = cleanErrorMessage(err);
      toast.error(errorMessage || "Failed to retry message. Please try again.", {
        position: "top-right",
        autoClose: 5000,
      });
      dispatch({
        type: "SET_ERROR",
        payload: err.message || "Failed to retry message",
      });
    }
  };

  if (!isCoFounder) {
    return (
      <main className="flex flex-col h-[86vh] w-full bg-white p-2 font-roboto">
        <header className="p-2 flex items-center justify-between bg-white">
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-gray-900">
              AI Assistant
            </h1>
            <p className="text-sm md:text-lg text-gray-500">
            Your Startup Success Partner
            </p>
          </div>
        </header>
        <div className="flex-1 flex items-center justify-center">
          <p className="text-gray-500">Chat is only available in AI Co-founder</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex flex-col h-[86vh] w-full bg-white p-2 font-roboto">
      <header className="p-2 grid grid-cols-[1fr_auto] gap-2 sm:gap-3 md:gap-4 items-center bg-white">
        <div className="min-w-0">
          <h1 className="text-base sm:text-md md:text-lg lg:text-xl font-bold text-gray-900 truncate">
            AI Co-founder
          </h1>
          <p className="text-[10px] text-xs md:text-base text-gray-500 truncate">
            Your Startup Success Partner
          </p>
        </div>
        <div className="flex items-center justify-end gap-1.5 sm:gap-2 md:gap-3 flex-shrink-0">
          {(() => {
            const totalLimit = typeof tokenStats.total === 'number' ? tokenStats.total : 20000;
            const usedValue = typeof tokenStats.used === 'number' ? tokenStats.used : 0;
            const exhausted = usedValue >= totalLimit && totalLimit > 0;

            if (exhausted) {
              return (
                <div className="min-w-[100px] md:min-w-[120px] lg:min-w-[160px] bg-red-50 border border-red-200 rounded-lg p-1.5 sm:p-2 md:p-3 shadow-sm">
                  <div className="flex items-center justify-center py-0.5 sm:py-1">
                    <AlertTriangle size={12} className="text-red-600 mr-1 sm:mr-1.5 md:mr-2 sm:w-3.5 sm:h-3.5 md:w-4 md:h-4" />
                    <span className="text-[9px] sm:text-xs md:text-sm font-semibold text-red-700">All tokens are used</span>
                  </div>
                </div>
              );
            }

            return (
              <div className="min-w-[100px] md:min-w-[120px] lg:min-w-[160px] bg-gray-50 border border-gray-300 rounded-lg p-1 sm:p-1.5 md:p-2 shadow-sm">
                <div className="flex items-center justify-center gap-1 sm:gap-1.5 md:gap-2 mb-0.5 sm:mb-1 md:mb-2">
                  <Gauge size={12} className="text-gray-600 sm:w-3.5 sm:h-3.5 md:w-4 md:h-4" />
                  <span className="text-[8px] sm:text-[10px] md:text-xs font-bold text-gray-700">Tokens</span>
                </div>
                <div className="flex items-stretch gap-2 sm:gap-3 md:gap-4 lg:gap-6 justify-center">
                  <div className="flex flex-col items-center">
                    <span className="text-[7px] sm:text-[9px] md:text-[11px] uppercase tracking-wide text-gray-500">Used</span>
                    <span className="text-xs sm:text-sm md:text-lg lg:text-xl font-mono tabular-nums font-semibold text-gray-900">{typeof tokenStats.used === 'number' ? tokenStats.used.toLocaleString() : (tokenStats.used ?? '—')}</span>
                  </div>
                  <div className="w-px bg-gray-200" />
                  <div className="flex flex-col items-center">
                    <span className="text-[7px] sm:text-[9px] md:text-[11px] uppercase tracking-wide text-gray-500">Total</span>
                    <span className="text-xs sm:text-sm md:text-lg lg:text-xl font-mono tabular-nums font-semibold text-gray-900">{typeof tokenStats.total === 'number' ? tokenStats.total.toLocaleString() : (tokenStats.total ?? '—')}</span>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden mt-2 bg-white rounded-xl shadow-lg relative">
        {/* Toggle Button for Mobile - Shows when sidebar is closed */}
        {!isStepsSidebarOpen && (
          <button
            onClick={() => setIsStepsSidebarOpen(true)}
            className="md:hidden absolute left-2 top-2 z-[60] bg-white border border-gray-300 rounded-lg p-2 shadow-md hover:bg-gray-50 transition-colors"
            aria-label="Open steps sidebar"
          >
            <ChevronRight size={20} className="text-gray-700" />
          </button>
        )}

        {/* Overlay for mobile when sidebar is open */}
        {isStepsSidebarOpen && (
          <div
            className="md:hidden fixed inset-0 z-[55]"
            onClick={() => setIsStepsSidebarOpen(false)}
            aria-hidden="true"
          />
        )}

        <aside
          className={`fixed md:static top-[168px] left-0 z-[60] md:z-auto bg-white border border-gray-200 flex-col rounded-l-xl md:rounded-l-xl transition-transform duration-300 ease-in-out ${
            isStepsSidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } md:translate-x-0 md:flex md:w-50 w-[280px] sm:w-[300px] h-full md:h-auto`}
        >
          <div className="p-4 border-b border-gray-300 flex items-center justify-between">
            <h2 className="font-semibold text-base sm:text-lg text-gray-800">Steps</h2>
            <div className="flex items-center gap-2">
              {/* Toggle Button for Mobile - Shows when sidebar is open */}
              <button
                onClick={() => setIsStepsSidebarOpen(false)}
                className="md:hidden cursor-pointer hover:text-gray-900 text-gray-600 hover:bg-gray-200 p-1 rounded-full transition-colors h-8 w-8 flex items-center justify-center"
                aria-label="Close steps sidebar"
              >
                <ChevronLeft size={18} className="text-gray-700" />
              </button>
              <button
                className="cursor-pointer hover:text-gray-900 text-gray-600 hover:bg-gray-200 p-1 rounded-full transition-colors h-8 w-8 md:h-11 md:w-11 text-xl md:text-3xl font-bold flex items-center justify-center"
                onClick={handleNewChat}
                disabled={state.status === "creating"}
                title="New Chat"
              >
                +
              </button>
            </div>
          </div>
          <div className="overflow-y-auto flex-1">
            {steps.map((step) => {
              const handleStepClick = async () => {
                setActiveStep(step.number);
                
                // Close sidebar on mobile when a step is clicked
                if (window.innerWidth < 768) {
                  setIsStepsSidebarOpen(false);
                }

                // Send message "Hi" for this step and show response in UI
                let chatId = state.currentChatId;

                // Create chat if it doesn't exist
                if (!chatId) {
                  try {
                    const { chatId: newChatId } = await chatService.createNewChat();
                    chatId = newChatId;
                    dispatch({ type: "SET_CURRENT_CHAT", payload: chatId });
                    await loadAllChats();
                  } catch (err) {
                    console.error('Failed to create chat for step click:', err);
                    const errorMessage = cleanErrorMessage(err);
                    toast.error(errorMessage || "Failed to create chat. Please try again.", {
                      position: "top-right",
                      autoClose: 5000,
                    });
                    return;
                  }
                }

                const content = "Hi";

                const userTimestamp = new Date().toLocaleString("en-US", {
                  hour: "numeric",
                  minute: "numeric",
                  hour12: true,
                  month: "short",
                  day: "numeric",
                });

                const userMsg = {
                  id: Date.now().toString(),
                  sender: "user",
                  text: content,
                  timestamp: userTimestamp,
                  file: null,
                };

                dispatch({ type: "ADD_MESSAGE", payload: userMsg });
                dispatch({ type: "SET_STATUS", payload: "sending" });

                try {
                  const stepParam = `entrepreneur_step_${step.number}`;
                  const response = await chatService.sendMessage(chatId, content, stepParam);

                  const aiTimestamp = new Date().toLocaleString("en-US", {
                    hour: "numeric",
                    minute: "numeric",
                    hour12: true,
                    month: "short",
                    day: "numeric",
                  });

                  // Extract text content from response.data, handling both string and object cases
                  let textContent = '';
                  if (response.type === 'general_response') {
                    if (typeof response.data === 'string') {
                      textContent = response.data;
                    } else if (response.data && typeof response.data === 'object') {
                      // If data is an object, check for text/message property (markdown), otherwise stringify
                      textContent = response.data.text || response.data.message || JSON.stringify(response.data, null, 2);
                    } else {
                      textContent = String(response.data ?? '');
                    }
                  }

                  const aiMsg = {
                    id: `${Date.now()}-ai`,
                    sender: "ai",
                    text: textContent,
                    type: response.type,
                    payload: response,
                    timestamp: aiTimestamp,
                  };

                  dispatch({ type: "ADD_MESSAGE", payload: aiMsg });
                  dispatch({ type: "SET_STATUS", payload: "idle" });

                  try {
                    const stats = await chatService.getTokenStats();
                    setTokenStats(stats);
                  } catch { }
                } catch (err) {
                  console.error('Failed to send step message:', err);
                  dispatch({ type: "MARK_MESSAGE_FAILED", payload: { id: userMsg.id } });
                  
                  // Handle 402 error: disable send button and show notification message
                  if (err.status === 402 && err.responseData) {
                    setIsSendDisabled(true);
                    const notificationMessage = err.responseData.notifiy || err.responseData.notify || "Token consumed, please buy the tokens";
                    toast.error(notificationMessage, {
                      position: "top-right",
                      autoClose: 5000,
                    });
                    dispatch({
                      type: "SET_ERROR",
                      payload: notificationMessage,
                    });
                    dispatch({ type: "SET_STATUS", payload: "idle" });
                    return;
                  }
                  
                  const errorMessage = cleanErrorMessage(err);
                  toast.error(errorMessage || "Failed to send message. Please try again.", {
                    position: "top-right",
                    autoClose: 5000,
                  });
                  dispatch({
                    type: "SET_ERROR",
                    payload: err.message || "Failed to send message",
                  });
                  dispatch({ type: "SET_STATUS", payload: "idle" });
                }
              };
              
              return (
                <div
                  key={step.number}
                  className={`p-2 hover:bg-gray-100 cursor-pointer border-b border-gray-200 text-xs sm:text-sm text-start text-gray-800 transition-colors ${activeStep === step.number ? "bg-gray-200 font-semibold" : ""
                    }`}
                  role="button"
                  tabIndex={0}
                  onClick={handleStepClick}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleStepClick();
                    }
                  }}
                >
                  <div className="font-semibold text-gray-900">
                    Step {step.number}: {step.title}
                  </div>
                </div>
              );
            })}
          </div>
        </aside>

        <section className="flex-1 flex flex-col w-full border border-gray-200 rounded-r-xl">
          {state.messages.length === 0 ? (
            <div className="flex-1 flex flex-col justify-center items-center px-4 text-center ">
              <p className="text-gray-500 text-sm md:text-base max-w-md">
                Hi there! I'm your AI Co-Founder — your personal guide through the entrepreneurial journey. We'll follow a powerful 7-step roadmap to turn your idea into a thriving business. Type "hi" to begin, and I'll guide you through it.
              </p>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6 flex flex-col gap-3">
              {state.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`w-full flex ${msg.sender === "ai" ? "justify-start" : "justify-end"
                    } px-2 mb-3`}
                >
                  <div
                    className={`max-w-full sm:max-w-md md:max-w-2xl p-3 rounded-xl shadow ${msg.sender === "ai"
                      ? "bg-gray-100 text-gray-800"
                      : "bg-blue-600 text-white"
                      }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span
                        className={`font-semibold text-sm ${msg.sender === "ai" ? "text-black" : "text-white"
                          }`}
                      >
                        {msg.sender === "ai" ? "AI Co-founder" : "You"}
                      </span>

                      <span
                        className={`text-xs ml-1 ${msg.sender === "ai" ? "text-black" : "text-white"
                          }`}
                      >
                        {msg.timestamp}
                      </span>
                    </div>
                    {msg.type === "entrepreneurial_response" && msg.payload ? (
                      <div className="">
                        <EntrepreneurialResponse payload={msg.payload} />
                      </div>
                    ) : msg.type === "image_response" && msg.payload?.logo ? (
                      <div className="flex flex-col gap-2">
                        <div className="relative group">
                          <img
                            src={msg.payload.logo}
                            alt="Generated logo"
                            className="max-w-full h-auto rounded-lg border border-gray-200 shadow-sm"
                            onError={(e) => {
                              e.target.style.display = 'none';
                              e.target.nextSibling.nextSibling.style.display = 'block';
                            }}
                          />
                          <button
                            onClick={() => handleImageDownload(msg.payload.logo)}
                            className="absolute top-2 right-2 bg-white/90 hover:bg-white p-2 rounded-full shadow-md transition-all opacity-0 group-hover:opacity-100 hover:scale-110"
                            title="Download image"
                          >
                            <Download size={20} className="text-gray-700" />
                          </button>
                          <p className="text-sm text-gray-600 mt-2" style={{ display: 'none' }}>
                            Failed to load image
                          </p>
                        </div>
                      </div>
                    ) : msg.type === "general_response" ? (
                      <div className="text-base md:text-md text-gray-700">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            p: ({ children }) => <p className="leading-relaxed mb-2">{children}</p>,
                            h1: ({ children }) => <h1 className="text-2xl font-bold text-gray-800 mt-4 mb-2">{children}</h1>,
                            h2: ({ children }) => <h2 className="text-xl font-bold text-gray-800 mt-4 mb-2">{children}</h2>,
                            h3: ({ children }) => <h3 className="text-md font-bold text-gray-800 mt-3 mb-2">{children}</h3>,
                            h4: ({ children }) => <h4 className="text-base font-semibold text-gray-800 mt-3 mb-1">{children}</h4>,
                            ul: ({ children }) => <ul className="list-disc list-inside ml-4 mb-2 space-y-1">{children}</ul>,
                            ol: ({ children }) => <ol className="list-decimal list-inside ml-4 mb-2 space-y-1">{children}</ol>,
                            li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                            strong: ({ children }) => <strong className="font-semibold text-gray-800">{children}</strong>,
                            em: ({ children }) => <em className="italic">{children}</em>,
                            code: ({ children, className }) => {
                              const isInline = !className;
                              return isInline ? (
                                <code className="bg-gray-200 px-1 py-0.5 rounded text-sm font-mono">{children}</code>
                              ) : (
                                <code className="block bg-gray-100 p-2 rounded text-sm font-mono overflow-x-auto">{children}</code>
                              );
                            },
                            blockquote: ({ children }) => (
                              <blockquote className="border-l-4 border-gray-300 pl-4 italic my-2">
                                {children}
                              </blockquote>
                            ),
                            a: ({ href, children }) => (
                              <a
                                href={href}
                                className="text-blue-600 hover:text-blue-800 underline"
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                {children}
                              </a>
                            ),
                            table: ({ children }) => (
                              <table className="w-full border-collapse my-3 text-sm md:text-base">
                                {children}
                              </table>
                            ),
                            thead: ({ children }) => (
                              <thead className="bg-gray-100">{children}</thead>
                            ),
                            tbody: ({ children }) => <tbody>{children}</tbody>,
                            tr: ({ children }) => (
                              <tr className="border-b border-gray-300 last:border-0">
                                {children}
                              </tr>
                            ),
                            th: ({ children }) => (
                              <th className="border border-gray-300 px-3 py-2 font-semibold text-left">
                                {children}
                              </th>
                            ),
                            td: ({ children }) => (
                              <td className="border border-gray-300 px-3 py-2 align-top">
                                {children}
                              </td>
                            ),
                          }}
                        >
                          {typeof msg.text === "string" ? msg.text : String(msg.text ?? "")}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <div className="text-base md:text-md text-white">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            p: ({ children }) => <p className="leading-relaxed mb-2">{children}</p>,
                            h1: ({ children }) => <h1 className="text-2xl font-bold mt-4 mb-2">{children}</h1>,
                            h2: ({ children }) => <h2 className="text-xl font-bold mt-4 mb-2">{children}</h2>,
                            h3: ({ children }) => <h3 className="text-lg font-bold mt-3 mb-2">{children}</h3>,
                            h4: ({ children }) => <h4 className="text-base font-semibold mt-3 mb-1">{children}</h4>,
                            ul: ({ children }) => <ul className="list-disc list-inside ml-4 mb-2 space-y-1">{children}</ul>,
                            ol: ({ children }) => <ol className="list-decimal list-inside ml-4 mb-2 space-y-1">{children}</ol>,
                            li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                            strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                            em: ({ children }) => <em className="italic">{children}</em>,
                            code: ({ children, className }) => {
                              const isInline = !className;
                              return isInline ? (
                                <code className="bg-white/20 px-1 py-0.5 rounded text-sm font-mono">
                                  {children}
                                </code>
                              ) : (
                                <code className="block bg-white/10 p-2 rounded text-sm font-mono overflow-x-auto">
                                  {children}
                                </code>
                              );
                            },
                            blockquote: ({ children }) => (
                              <blockquote className="border-l-4 border-white/30 pl-4 italic my-2">
                                {children}
                              </blockquote>
                            ),
                            a: ({ href, children }) => (
                              <a
                                href={href}
                                className="text-blue-200 hover:text-blue-100 underline"
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                {children}
                              </a>
                            ),
                            table: ({ children }) => (
                              <table className="w-full border-collapse my-3 text-sm md:text-base">
                                {children}
                              </table>
                            ),
                            thead: ({ children }) => (
                              <thead className="bg-white/10">{children}</thead>
                            ),
                            tbody: ({ children }) => <tbody>{children}</tbody>,
                            tr: ({ children }) => (
                              <tr className="border-b border-white/30 last:border-0">
                                {children}
                              </tr>
                            ),
                            th: ({ children }) => (
                              <th className="border border-white/40 px-3 py-2 font-semibold text-left">
                                {children}
                              </th>
                            ),
                            td: ({ children }) => (
                              <td className="border border-white/30 px-3 py-2 align-top">
                                {children}
                              </td>
                            ),
                          }}
                        >
                          {typeof msg.text === "string" ? msg.text : String(msg.text ?? "")}
                        </ReactMarkdown>
                      </div>
                    )}
                    {msg.file && (
                      <div className="mt-1 flex items-center gap-2">
                        <span className="text-xs truncate max-w-xs">
                          {msg.file.name}
                        </span>
                      </div>
                    )}
                    {msg.sender === 'user' && msg.failed && (
                      <div className="mt-2 flex justify-start">
                        <button
                          type="button"
                          title="Retry"
                          onClick={() => handleRetrySend(msg)}
                          className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs border cursor-pointer transition-colors text-white hover:text-white bg-red-500/80 hover:bg-red-600/80 border-red-500/20`}
                        >
                          <RotateCcw size={16} />
                          <span>Retry</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {state.status === "sending" && <ThinkingLoader />}
              <div ref={messagesEndRef} />
            </div>
          )}
          <form
            className="p-3 md:p-4 border-t border-gray-200 rounded-b-lg bg-gray-50 flex-shrink-0"
            onSubmit={handleSend}
          >
            <div className="flex flex-wrap items-center bg-white border border-gray-300 rounded-full px-3 py-2 shadow-sm w-full">
              <input
                type="text"
                placeholder="Type a message..."
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                className="flex-1 min-w-0 outline-none bg-transparent text-gray-800 placeholder-gray-400 text-sm md:text-lg"
              />

              {uploadingFile && (
                <span className="text-sm truncate max-w-[120px] sm:max-w-[60px] md:max-w-[120px] ml-2">
                  {uploadingFile.name}
                </span>
              )}

              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                onChange={handleFileChange}
              />

              {/* <div className="relative ml-2 flex-shrink-0">
                <button
                  type="button"
                  onClick={() => fileInputRef.current.click()}
                  className="cursor-pointer text-gray-500 hover:text-gray-700 p-2 rounded-full bg-gray-200 h-10 w-10 hover:bg-gray-300 transition-colors flex items-center justify-center relative"
                >
                  <FolderUp />
                </button>

                {uploadingFile && (
                  <>
                    <svg
                      className="absolute top-0 left-0 w-10 h-10"
                      viewBox="0 0 36 36"
                    >
                      <circle className="text-gray-300" strokeWidth="4" stroke="currentColor" fill="transparent" r="16" cx="18" cy="18" />
                      <circle className="text-green-400" strokeWidth="4" strokeDasharray="100" strokeDashoffset={100 - uploadProgress} strokeLinecap="round" stroke="currentColor" fill="transparent" r="16" cx="18" cy="18" />
                    </svg>
                    <button
                      type="button"
                      onClick={() => {
                        setUploadingFile(null);
                        setUploadProgress(0);
                        if (fileInputRef.current)
                          fileInputRef.current.value = "";
                      }}
                      className="absolute -top-1 -right-1 bg-red-500 rounded-full p-1 shadow hover:bg-red-600 cursor-pointer"
                    >
                      <X size={14} className="text-black" />
                    </button>
                  </>
                )}
              </div> */}

              <button
                type="submit"
                disabled={state.status === "sending" || isSendDisabled}
                className="cursor-pointer ml-2 text-blue-600 hover:text-blue-800 p-2 rounded-full bg-blue-200 h-10 w-10 hover:bg-blue-300 transition-colors disabled:opacity-50 flex-shrink-0"
              >
                <Send size={20} />
              </button>
            </div>

            
          </form>
        </section>
      </div>
    </main>
  );
};

export default ChatWindow;
