import { authFetch } from './authService';

const BASE_URL = import.meta.env.VITE_CHAT_API_BASE_URL;

export const chatService = {
  getAllChats: async () => {
    const url = `${BASE_URL}/api/chat/history/`;
    const response = await authFetch(url, { method: 'GET' });

    if (!response.ok) {
      throw new Error(`Failed to get chat history: ${response.status}`);
    }

    const data = await response.json();
    const chats = data?.message || [];

    return chats.map(item => ({
      id: item?.detail?.chat_id,
      name: item?.detail?.chat_name || 'New Chat',
      timestamp: new Date().toISOString()
    })).filter(chat => chat.id);
  },

  createNewChat: async () => {
    const url = `${BASE_URL}/api/chat/new-chat/`;
    const response = await authFetch(url, { method: 'GET' });

    if (!response.ok) {
      throw new Error(`Failed to create new chat: ${response.status}`);
    }

    const data = await response.json();
    return {
      chatId: data?.message?.chat_id,
      chatName: data?.message?.chat_name || 'New Chat'
    };
  },

  sendMessage: async (chatId, userInput, step = null) => {
    const url = `${BASE_URL}/api/chat/structured-agent/?chat-id=${encodeURIComponent(chatId)}`;
    const requestBody = { user_input: userInput };
    if (step) {
      requestBody.step = step;
    }
    const response = await authFetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      // For 402 errors, extract the response body to get the notification message
      if (response.status === 402) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          try {
            const text = await response.text();
            errorData = JSON.parse(text);
          } catch {
            errorData = {};
          }
        }
        const error = new Error(`Failed to send message: ${response.status}`);
        error.status = 402;
        error.responseData = errorData;
        throw error;
      }
      throw new Error(`Failed to send message: ${response.status}`);
    }

    const data = await response.json();
    const message = data?.message || {};
    
    // Handle new response format: { message: { step: "...", response: "..." } }
    // Extract the response field as the data to display
    return {
      type: message.type || 'general_response',
      data: message.response || message.data || '',
      step: message.step,
      ...message
    };
  },

  getChatMessages: async (chatId) => {
    const url = `${BASE_URL}/api/chat/history/?chat-id=${encodeURIComponent(chatId)}`;
    const response = await authFetch(url, { method: 'GET' });

    if (!response.ok) {
      throw new Error(`Failed to get chat messages: ${response.status}`);
    }

    const result = await response.json();
    const messages = result?.message || [];

    return messages.map((msg, index) => {
      if (msg.user) {
        return {
          id: `user-${index}`,
          sender: 'user',
          text: msg.user,
          timestamp: new Date().toLocaleString('en-US', {
            hour: 'numeric',
            minute: 'numeric',
            hour12: true,
            month: 'short',
            day: 'numeric'
          })
        };
      } else if (msg.agent) {
        let textContent = '';
        let agentType = 'general_response';
        if (typeof msg.agent === 'string') {
          textContent = msg.agent;
        } else if (msg.agent.type === 'general_response') {
          agentType = 'general_response';
          if (typeof msg.agent.data === 'string') {
            textContent = msg.agent.data;
          } else if (msg.agent.data && typeof msg.agent.data === 'object') {
            textContent = msg.agent.data.text || msg.agent.data.message || JSON.stringify(msg.agent.data, null, 2);
          } else {
            textContent = String(msg.agent.data ?? '');
          }
        } else if (msg.agent.type) {
          agentType = msg.agent.type;
          if (typeof msg.agent.data === 'string') {
            textContent = msg.agent.data;
          } else if (msg.agent.data && typeof msg.agent.data === 'object') {
            textContent = msg.agent.data.text || msg.agent.data.message || JSON.stringify(msg.agent.data, null, 2);
          } else {
            textContent = String(msg.agent.data ?? '');
          }
        } else {
          textContent = msg.agent.text || msg.agent.message || String(msg.agent);
        }

        return {
          id: `agent-${index}`,
          sender: 'ai',
          type: agentType,
          text: textContent,
          payload: msg.agent,
          timestamp: new Date().toLocaleString('en-US', {
            hour: 'numeric',
            minute: 'numeric',
            hour12: true,
            month: 'short',
            day: 'numeric'
          })
        };
      }
      return null;
    }).filter(Boolean);
  },

  getTokenStats: async () => {
    const url = `${BASE_URL}/api/chat/token/`;
    const response = await authFetch(url, { method: 'GET' });

    if (!response.ok) {
      throw new Error(`Failed to get token stats: ${response.status}`);
    }

    const data = await response.json();
    const payload = data?.message ?? data ?? {};

    const used = payload.used ?? payload.tokens_used ?? payload.used_tokens ?? payload.token_used ?? null;
    const total = payload.total ?? payload.total_tokens ?? payload.tokens_total ?? payload.total_token ?? null;

    return { used, total };
  }
};

