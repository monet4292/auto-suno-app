/**
 * Suno API Client - Node.js Implementation
 * Migration from Python's src/core/suno_api_client.py
 */

const axios = require('axios');

class SunoApiClient {
  /**
   * API Client for Suno.com interactions
   * Handles profile clips fetching, user information, and rate limiting
   */

  constructor(sessionToken = null, proxyList = []) {
    this.sessionToken = sessionToken;
    this.proxyList = proxyList;
    this.baseURL = 'https://studio-api.prod.suno.com/api';

    // Setup headers
    this.headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      'Accept': 'application/json',
    };

    if (this.sessionToken) {
      this.headers['Authorization'] = `Bearer ${this.sessionToken}`;
    }

    // Rate limiting state
    this.lastRequestTime = 0;
    this.rateLimitWait = 10;
  }

  /**
   * Get a random proxy from the proxy list
   */
  getRandomProxy() {
    if (this.proxyList.length === 0) {
      return null;
    }
    const proxyURL = this.proxyList[Math.floor(Math.random() * this.proxyList.length)];
    return {
      http: proxyURL,
      https: proxyURL
    };
  }

  /**
   * Handle rate limiting from API responses
   */
  handleRateLimit(response) {
    if (response.status === 429) {
      console.warn(`Rate limit hit (429), waiting ${this.rateLimitWait}s...`);

      // In Node.js, we'll return the wait time instead of sleeping
      const waitTime = this.rateLimitWait;
      this.rateLimitWait = Math.min(this.rateLimitWait + 5, 60); // Exponential backoff

      return { shouldRetry: true, waitTime };
    }

    // Reset rate limit wait on successful request
    if (response.status === 200) {
      this.rateLimitWait = 10;
    }

    return { shouldRetry: false, waitTime: 0 };
  }

  /**
   * Make an HTTP request with error handling and rate limiting
   */
  async makeRequest(method, endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    // Setup request config
    const config = {
      method: method.toLowerCase(),
      url: url,
      headers: { ...this.headers, ...options.headers },
      timeout: options.timeout || 30000,
      ...options
    };

    // Add proxies if available
    if (config.proxies === undefined && this.proxyList.length > 0) {
      config.proxy = this.getRandomProxy();
    }

    try {
      // Rate limiting: ensure minimum delay between requests
      const now = Date.now();
      const elapsed = now - this.lastRequestTime;
      if (elapsed < 2000) { // Minimum 2 seconds between requests
        await this.sleep(2000 - elapsed);
      }

      const response = await axios(config);
      this.lastRequestTime = Date.now();

      // Handle rate limiting
      const rateLimitInfo = this.handleRateLimit(response);
      if (rateLimitInfo.shouldRetry) {
        console.log(`Retrying after ${rateLimitInfo.waitTime}s...`);
        await this.sleep(rateLimitInfo.waitTime * 1000);

        // Retry once after rate limit
        const retryResponse = await axios(config);
        this.lastRequestTime = Date.now();
        return retryResponse.data;
      }

      return response.data;

    } catch (error) {
      console.error(`API request failed: ${method.toUpperCase()} ${endpoint} - ${error.message}`);

      if (error.response) {
        // Handle HTTP errors
        const rateLimitInfo = this.handleRateLimit(error.response);
        if (rateLimitInfo.shouldRetry) {
          console.log(`Retrying after rate limit: ${rateLimitInfo.waitTime}s...`);
          await this.sleep(rateLimitInfo.waitTime * 1000);
          return this.makeRequest(method, endpoint, options);
        }
      }

      throw error;
    }
  }

  /**
   * Sleep utility function
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Update session token
   */
  updateSessionToken(token) {
    this.sessionToken = token;
    if (token) {
      this.headers['Authorization'] = `Bearer ${token}`;
    } else {
      delete this.headers['Authorization'];
    }
  }

  /**
   * Fetch clips from a user profile with pagination
   */
  async fetchProfileClips(profileName, startPage = 0, maxPages = null) {
    console.log(`Fetching clips from profile: ${profileName} (starting page ${startPage})`);

    // Remove @ prefix if present
    const cleanProfileName = profileName.startsWith('@')
      ? profileName.substring(1)
      : profileName;

    const endpoint = `/profiles/${cleanProfileName}/clips`;
    const allClips = [];
    let page = startPage;
    let pagesFetched = 0;

    while (true) {
      // Check page limit
      if (maxPages && pagesFetched >= maxPages) {
        console.log(`Reached maximum pages limit: ${maxPages}`);
        break;
      }

      try {
        const data = await this.makeRequest('GET', endpoint, {
          params: { page }
        });

        if (!data) {
          console.error(`Failed to fetch page ${page}`);
          return allClips;
        }

        const clips = data.clips || [];
        if (clips.length === 0) {
          console.log(`No more clips found at page ${page}`);
          break;
        }

        allClips.push(...clips);
        console.log(`Page ${page}: ${clips.length} clips`);
        page += 1;
        pagesFetched += 1;

        // Delay between pages
        if (pagesFetched < (maxPages || Infinity)) {
          await this.sleep(5000);
        }

      } catch (error) {
        console.error(`Error fetching page ${page}:`, error.message);
        break;
      }
    }

    return allClips;
  }

  /**
   * Fetch current user's clips from /feed/v2
   */
  async fetchMyClips() {
    console.log('Fetching current user\'s clips from /feed/v2');

    try {
      const data = await this.makeRequest('GET', '/feed/v2', {
        params: { page: 0 }
      });

      if (!data) {
        console.error('Failed to fetch user clips');
        return [];
      }

      const clips = data.clips || [];
      console.log(`Fetched ${clips.length} user clips`);
      return clips;

    } catch (error) {
      console.error('Error fetching user clips:', error.message);
      return [];
    }
  }

  /**
   * Get current user information
   */
  async getCurrentUserInfo() {
    try {
      const data = await this.makeRequest('GET', '/billing/info');
      return data;

    } catch (error) {
      console.error('Error fetching user info:', error.message);
      return null;
    }
  }

  /**
   * Fetch clip by UUID
   */
  async fetchClipById(clipId) {
    try {
      const data = await this.makeRequest('GET', `/clips/${clipId}`);
      return data;

    } catch (error) {
      console.error(`Error fetching clip ${clipId}:`, error.message);
      return null;
    }
  }

  /**
   * Fetch clips from /create page with pagination
   */
  async fetchCreateClipsPaginated(startPage = 0, maxPages = null) {
    console.log(`Fetching clips from /create (starting page ${startPage})`);

    const allClips = [];
    let page = startPage;
    let pagesFetched = 0;
    let hasMore = true;

    while (hasMore) {
      // Check page limit
      if (maxPages && pagesFetched >= maxPages) {
        console.log(`Reached maximum pages limit: ${maxPages}`);
        break;
      }

      try {
        // This would be similar to fetchMyClips but with pagination
        const data = await this.makeRequest('GET', '/feed/v2', {
          params: { page }
        });

        if (!data) {
          console.error(`Failed to fetch create page ${page}`);
          break;
        }

        const clips = data.clips || [];
        if (clips.length === 0) {
          console.log(`No more clips found at page ${page}`);
          hasMore = false;
          break;
        }

        allClips.push(...clips);
        console.log(`Create page ${page}: ${clips.length} clips`);

        page += 1;
        pagesFetched += 1;

        // Delay between pages
        await this.sleep(5000);

        // Determine if there are more pages (this would depend on API response)
        hasMore = clips.length > 0; // Simplified logic

      } catch (error) {
        console.error(`Error fetching create page ${page}:`, error.message);
        break;
      }
    }

    return {
      clips: allClips,
      lastPage: page - 1,
      hasMore
    };
  }
}

module.exports = SunoApiClient;