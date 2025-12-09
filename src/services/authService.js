import { tokenStorage } from "../utils/tokenStorage";

const BASE_URL = import.meta.env.VITE_CHAT_API_BASE_URL;
const AUTH_ENDPOINT = `${BASE_URL}/api/bubble/auth/`;
const REFRESH_ENDPOINT = `${BASE_URL}/api/bubble/refresh/`;
const EXTERNAL_DASHBOARD_URL = import.meta.env.VITE_EXTERNAL_DASHBOARD_URL;

export const authService = {
  getSidForAuth: () => {
    // Prefer stored sid; if missing, try reading from current URL (query or hash), then persist
    let sid = tokenStorage.getSid();
    console.log("🔍 getSidForAuth - SID from storage:", sid);
    if (!sid) {
      try {
        const search =
          typeof window !== "undefined" ? window.location.search : "";
        const hash = typeof window !== "undefined" ? window.location.hash : "";
        const fromSearch = new URLSearchParams(search).get("sid");
        const fromHash =
          hash && hash.includes("sid=")
            ? new URLSearchParams(
                hash.replace(/^#\/?/, "").split("?")[1] ||
                  hash.replace(/^#\/?/, "")
              ).get("sid")
            : null;
        console.log("🔍 getSidForAuth - URL search:", search, "hash:", hash);
        console.log("🔍 getSidForAuth - SID from search:", fromSearch, "from hash:", fromHash);
        sid = fromSearch || fromHash || null;
        if (sid) {
          console.log("💾 Saving SID to storage:", sid);
          tokenStorage.setSid(sid);
        }
      } catch (error) {
        console.error("❌ Error getting SID from URL:", error);
      }
    }
    console.log("🔍 getSidForAuth - Final SID:", sid);
    return sid || null;
  },

  authenticateWithSid: async (sid) => {
    const url = `${AUTH_ENDPOINT}?sid=${encodeURIComponent(sid)}`;
    const response = await fetch(url, { method: "GET" });

    if (!response.ok) {
      throw new Error(`Authentication failed: ${response.status}`);
    }

    const data = await response.json();

    const accessToken =
      data?.messsage?.access || data?.message?.access || data?.access;
    const refreshToken =
      data?.messsage?.refresh || data?.message?.refresh || data?.refresh;

    if (!accessToken) {
      throw new Error("No access token received from server");
    }

    return { accessToken, refreshToken };
  },

  refreshAccessToken: async (refreshToken) => {
    const response = await fetch(REFRESH_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      throw new Error(`Token refresh failed: ${response.status}`);
    }

    const data = await response.json();
    const newAccessToken =
      data?.message?.access || data?.access || data?.token || data?.jwt;
    // Also extract new refresh token if provided (some APIs rotate refresh tokens)
    const newRefreshToken =
      data?.message?.refresh || data?.refresh || refreshToken;

    if (!newAccessToken) {
      throw new Error("No access token received from refresh");
    }

    return { accessToken: newAccessToken, refreshToken: newRefreshToken };
  },

  initializeAuth: async () => {
    // 1️⃣ First: get SID and make a request (authenticate with SID)
    const sid = authService.getSidForAuth();
    console.log("🔍 initializeAuth - SID found:", sid);

    if (sid) {
      console.log("📞 Calling authenticateWithSid API with SID:", sid);
      const { accessToken, refreshToken } = await authService.authenticateWithSid(
        sid
      );

      tokenStorage.setTokens(accessToken, refreshToken, sid);
      return accessToken;
    }

    // 2️⃣ If SID not found → check access and refresh token
    console.log("⚠️ SID not found, checking existing tokens...");
      const existingToken = tokenStorage.getAccessToken();
      const existingRefreshToken = tokenStorage.getRefreshToken();
    console.log("🔍 Existing tokens - access:", !!existingToken, "refresh:", !!existingRefreshToken);

      if (existingToken && existingRefreshToken) {
      console.log("✅ Using existing tokens, skipping SID API call");
        return existingToken;
      }

    // 3️⃣ If access and refresh not found → redirect to external dashboard
      if (EXTERNAL_DASHBOARD_URL) {
        window.location.href = EXTERNAL_DASHBOARD_URL;
        return null;
      }

      throw new Error("Missing session id (sid)");
  },

  logout: () => {
    tokenStorage.clearTokens();
    window.location.reload();
  },
};

export { EXTERNAL_DASHBOARD_URL };

export const authFetch = async (input, init = {}) => {
  let token = tokenStorage.getAccessToken();
  // If no access token yet, authenticate first using SID
  if (!token) {
    try {
      const accessToken = await authService.initializeAuth();
      // If initializeAuth redirected, accessToken will be null
      if (!accessToken) {
        // Redirect already happened, return a response that won't be used
        return new Response(null, { status: 302 });
      }
      token = accessToken;
    } catch (e) {
      // If redirect happened, don't proceed
      if (
        EXTERNAL_DASHBOARD_URL &&
        window.location.href !== EXTERNAL_DASHBOARD_URL
      ) {
        return new Response(null, { status: 302 });
      }
      // proceed; server may still allow public endpoints
    }
  }
  const maxUnauthorizedAttempts = 2;
  // keep an in-memory counter across calls
  authFetch._unauthorizedAttempts = authFetch._unauthorizedAttempts || 0;

  const makeRequest = (authToken) => {
    const headers = {
      "Content-Type": "application/json",
      ...(init.headers || {}),
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    };

    return fetch(input, { ...init, headers });
  };

  let response = await makeRequest(token);

  if (response.status === 401) {
    authFetch._unauthorizedAttempts += 1;
    if (authFetch._unauthorizedAttempts >= maxUnauthorizedAttempts) {
      // redirect to external dashboard after two failed attempts (disabled for now)
      // if (EXTERNAL_DASHBOARD_URL) window.location.href = EXTERNAL_DASHBOARD_URL;
      throw new Error("Unauthorized");
    }
    const refreshToken = tokenStorage.getRefreshToken();
    const sid = tokenStorage.getSid();

    if (!refreshToken) {
      // Try authenticating using sid once before redirecting
      try {
        const sidForAuth = authService.getSidForAuth();
        if (!sidForAuth) throw new Error("No SID");
        const { accessToken, refreshToken: newRefresh } =
          await authService.authenticateWithSid(sidForAuth);
        token = accessToken;
        tokenStorage.setTokens(accessToken, newRefresh, sidForAuth);
        // Reset unauthorized attempts counter on successful auth
        authFetch._unauthorizedAttempts = 0;
        response = await makeRequest(token);
      } catch (e) {
        // if (EXTERNAL_DASHBOARD_URL) window.location.href = EXTERNAL_DASHBOARD_URL; // disabled
        throw e;
      }
    } else {
      try {
        const { accessToken: newAccessToken, refreshToken: newRefreshToken } =
          await authService.refreshAccessToken(refreshToken);
        // Store both new access token and new refresh token (if rotated)
        tokenStorage.setTokens(newAccessToken, newRefreshToken, sid);
        // Reset unauthorized attempts counter on successful refresh
        authFetch._unauthorizedAttempts = 0;
        token = newAccessToken;
        response = await makeRequest(newAccessToken);
      } catch (error) {
        console.error("Token refresh error:", error);
        // Attempt SID auth before redirect
        try {
          const sidForAuth = authService.getSidForAuth();
          if (!sidForAuth) throw new Error("No SID");
          const { accessToken, refreshToken: newRefresh } =
            await authService.authenticateWithSid(sidForAuth);
          tokenStorage.setTokens(accessToken, newRefresh, sidForAuth);
          // Reset unauthorized attempts counter on successful auth
          authFetch._unauthorizedAttempts = 0;
          token = accessToken;
          response = await makeRequest(accessToken);
        } catch (e) {
          // if (EXTERNAL_DASHBOARD_URL) window.location.href = EXTERNAL_DASHBOARD_URL; // disabled
          throw e;
        }
      }
    }
  } else {
    // Reset unauthorized attempts counter on successful request
    authFetch._unauthorizedAttempts = 0;
  }

  return response;
};
