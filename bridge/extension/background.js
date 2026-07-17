// Chrome Bridge - Chrome Extension Background Worker
// Connects to local WebSocket server and executes browser commands
// Version: 2.0 — added scroll/get_url/press_key/find_element, real screenshot, alarms keepalive

let WS_URL = 'ws://127.0.0.1:19876';
let ws = null;
let reconnectTimer = null;
{
  // Read WS port from storage (set via 'set_ws_port' command)
  chrome.storage.local.get(['ws_port'], (result) => {
    if (result.ws_port) {
      WS_URL = `ws://127.0.0.1:${result.ws_port}`;
    }
  });
}

// ==================== WebSocket Connection ====================

function connect() {
  if (ws && ws.readyState === WebSocket.OPEN) return;

  console.log('[CB] Connecting to', WS_URL);
  try {
    ws = new WebSocket(WS_URL);
  } catch (e) {
    console.error('[CB] WebSocket creation failed:', e.message);
    scheduleReconnect();
    return;
  }

  ws.onopen = () => {
    console.log('[CB] Connected to bridge server');
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };

  ws.onmessage = async (event) => {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch (e) {
      console.error('[CB] Invalid message');
      return;
    }

    const { id, cmd, args } = msg;
    console.log('[CB] Received:', cmd);

    let result;
    try {
      switch (cmd) {
        case 'ping':
          result = { ok: true, pong: true };
          break;
        case 'version':
          result = { ok: true, version: '1.0', commands: 'ping,version,new_tab,navigate,list_tabs,find_tab,close_tab,get_url,activate_tab,reload,go_back,go_forward,click,click_text,double_click,right_click,hover,type,type_active,type_trusted,press_key,scroll,select_option,find_element,get_attribute,get_content,get_html,screenshot,eval,wait,wait_for_element,fetch_api,get_images,get_cookies,set_cookie,get_storage,set_storage,handle_dialog,file_chooser_intercept,reload_self' };
          break;
        case 'reload_self':
          // Reload the extension (service worker restarts, connection drops)
          chrome.runtime.reload();
          result = { ok: true, msg: 'reloading' };
          break;
        case 'set_ws_port':
          // Change WebSocket port and reconnect
          {
            const port = args.port || 19876;
            chrome.storage.local.set({ ws_port: port });
            WS_URL = `ws://127.0.0.1:${port}`;
            console.log('[CB] WS port changed to', port, '- reconnecting...');
            if (ws) { try { ws.close(); } catch(e) {} }
            ws = null;
            connect();
            result = { ok: true, port };
          }
          break;
        case 'new_tab':
          result = await handleNewTab(args);
          break;
        case 'navigate':
          result = await handleNavigate(args);
          break;
        case 'list_tabs':
          result = await handleListTabs();
          break;
        case 'find_tab':
          result = await handleFindTab(args);
          break;
        case 'close_tab':
          result = await handleCloseTab(args);
          break;
        case 'click':
          result = await handleClick(args);
          break;
        case 'click_text':
          result = await handleClickText(args);
          break;
        case 'type':
          result = await handleType(args);
          break;
        case 'get_content':
          result = await handleGetContent(args);
          break;
        case 'get_url':
          result = await handleGetUrl(args);
          break;
        case 'eval':
          result = await handleEval(args);
          break;
        case 'screenshot':
          result = await handleScreenshot(args);
          break;
        case 'scroll':
          result = await handleScroll(args);
          break;
        case 'press_key':
          result = await handlePressKey(args);
          break;
        case 'find_element':
          result = await handleFindElement(args);
          break;
        case 'wait':
          result = await handleWait(args);
          break;
        case 'fetch_api':
          result = await handleFetchApi(args);
          break;
        case 'type_active':
          result = await handleTypeActive(args);
          break;
        case 'type_trusted':
          result = await handleTypeTrusted(args);
          break;
        case 'file_chooser_intercept':
          result = await handleFileChooserIntercept(args);
          break;
        case 'activate_tab':
          result = await chrome.tabs.update(args.tab_id, { active: true });
          result = { ok: true, tabId: result.id, active: true };
          break;
        case 'get_images':
          result = await handleGetImages(args);
          break;
        // Mouse
        case 'hover':
          result = await handleHover(args);
          break;
        case 'double_click':
          result = await handleDoubleClick(args);
          break;
        case 'right_click':
          result = await handleRightClick(args);
          break;
        // Form
        case 'select_option':
          result = await handleSelectOption(args);
          break;
        // Navigation
        case 'go_back':
          result = await handleGoBack(args);
          break;
        case 'go_forward':
          result = await handleGoForward(args);
          break;
        case 'reload':
          result = await handleReload(args);
          break;
        // Content
        case 'get_html':
          result = await handleGetHtml(args);
          break;
        case 'get_attribute':
          result = await handleGetAttribute(args);
          break;
        // Wait
        case 'wait_for_element':
          result = await handleWaitForElement(args);
          break;
        // Dialogs
        case 'handle_dialog':
          result = await handleDialog(args);
          break;
        // Cookies & Storage
        case 'get_cookies':
          result = await handleGetCookies(args);
          break;
        case 'set_cookie':
          result = await handleSetCookie(args);
          break;
        case 'get_storage':
          result = await handleGetStorage(args);
          break;
        case 'set_storage':
          result = await handleSetStorage(args);
          break;
        default:
          result = { ok: false, error: 'Unknown command: ' + cmd };
      }
    } catch (e) {
      console.error('[CB] Command error:', e.message);
      result = { ok: false, error: e.message };
      // Add troubleshooting hints for common errors
      const hints = {
        'Element not found': 'Try get_content to verify page text, or wait_for_element to wait for dynamic content',
        'No active tab': 'Open a tab first with new_tab url=...',
        'No active tab to close': 'Open a tab first or specify tab_id',
        'Option not found': 'Try get_content to see available options, or use select_option with text=...',
      };
      for (const [pattern, hint] of Object.entries(hints)) {
        if (result.error && result.error.includes(pattern)) {
          result.hint = hint;
          break;
        }
      }
    }

    sendResponse(id, result);
  };

  ws.onclose = () => {
    console.log('[CB] Disconnected');
    ws = null;
    scheduleReconnect();
  };

  ws.onerror = () => {
    console.log('[CB] Connection error');
  };
}

function scheduleReconnect() {
  if (!reconnectTimer) {
    reconnectTimer = setTimeout(connect, 2000);
  }
}

function sendResponse(id, data) {
  try {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ id: id, ok: data.ok, data: data }));
    }
  } catch (e) {
    console.error('[CB] Failed to send response:', e.message);
  }
}

// ==================== Command Handlers ====================

async function handleNewTab(args) {
  const tab = await chrome.tabs.create({ url: args.url || 'about:blank' });
  return { ok: true, tabId: tab.id, url: tab.url, title: tab.title };
}

async function handleNavigate(args) {
  let tabId = args.tab_id;
  if (!tabId) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return { ok: false, error: 'No active tab' };
    tabId = tab.id;
  }
  await chrome.tabs.update(tabId, { url: args.url });
  // Wait for page load (with timeout)
  await new Promise(r => {
    let resolved = false;
    const listener = (tid, changeInfo) => {
      if (!resolved && tid === tabId && changeInfo.status === 'complete') {
        resolved = true;
        chrome.tabs.onUpdated.removeListener(listener);
        r();
      }
    };
    chrome.tabs.onUpdated.addListener(listener);
    setTimeout(() => {
      if (!resolved) {
        chrome.tabs.onUpdated.removeListener(listener);
        r();
      }
    }, 30000);
  });
  const tab = await chrome.tabs.get(tabId);
  return { ok: true, tabId: tab.id, url: tab.url, title: tab.title };
}

async function handleListTabs() {
  const tabs = await chrome.tabs.query({});
  const list = tabs.map(t => ({ id: t.id, title: t.title, url: t.url, active: t.active }));
  return { ok: true, tabs: list };
}

async function handleFindTab(args) {
  const keyword = (args.keyword || '').toLowerCase();
  if (!keyword) return { ok: false, error: 'keyword is required' };
  const tabs = await chrome.tabs.query({});
  const matched = tabs.filter(t => {
    const title = (t.title || '').toLowerCase();
    const url = (t.url || '').toLowerCase();
    return title.includes(keyword) || url.includes(keyword);
  }).map(t => ({ id: t.id, title: t.title, url: t.url, active: t.active }));

  if (matched.length === 0) {
    return { ok: false, error: `No tab found matching: ${keyword}`, count: 0 };
  }
  // Return the first match's tabId for convenience, plus full list
  return { ok: true, tabId: matched[0].id, count: matched.length, tabs: matched };
}

async function handleCloseTab(args) {
  let tabId = args.tab_id;
  if (!tabId) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return { ok: false, error: 'No active tab to close' };
    tabId = tab.id;
  }
  await chrome.tabs.remove(tabId);
  return { ok: true };
}

async function handleClick(args) {
  const tabId = args.tab_id || await getActiveTabId();
  await chrome.scripting.executeScript({
    target: { tabId },
    func: (sel) => {
      const el = document.querySelector(sel);
      if (!el) throw new Error('Element not found: ' + sel);
      el.scrollIntoView({ behavior: 'instant', block: 'center' });
      el.click();
    },
    args: [args.selector]
  });
  return { ok: true };
}

async function handleClickText(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const mode = args.mode || 'exact'; // 'exact' or 'contains'
  await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (text, matchMode) => {
      const elements = document.querySelectorAll('span, button, div, li, a, label, p, h1, h2, h3, h4, td, th');
      for (const el of elements) {
        const elText = el.textContent.trim();
        const match = matchMode === 'contains' ? elText.includes(text) : elText === text;
        if (match) {
          el.scrollIntoView({ behavior: 'instant', block: 'center' });
          el.click();
          return 'clicked: ' + elText.substring(0, 50);
        }
      }
      throw new Error('Element not found with text: ' + text);
    },
    args: [args.text, mode]
  });
  return { ok: true };
}

async function handleType(args) {
  const tabId = args.tab_id || await getActiveTabId();
  await chrome.scripting.executeScript({
    target: { tabId },
    func: (sel, txt) => {
      const el = document.querySelector(sel);
      if (!el) throw new Error('Element not found: ' + sel);
      el.focus();
      el.value = txt;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    },
    args: [args.selector, args.text]
  });
  return { ok: true };
}

async function handleGetContent(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      const body = document.body;
      if (!body) return '(empty)';
      const clone = body.cloneNode(true);
      clone.querySelectorAll('script, style, noscript, svg, iframe').forEach(el => el.remove());
      let text = clone.innerText || clone.textContent || '';
      return text;
    }
  });
  return { ok: true, text: result.result };
}

async function handleGetUrl(args) {
  if (args.tab_id) {
    const tab = await chrome.tabs.get(args.tab_id);
    return { ok: true, url: tab.url, title: tab.title, tabId: tab.id };
  }
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return { ok: false, error: 'No active tab' };
  return { ok: true, url: tab.url, title: tab.title, tabId: tab.id };
}

async function handleEval(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (code) => {
      return new Promise((resolve) => {
        try {
          const callbackId = '__cbe_' + Math.random().toString(36).slice(2);
          const script = document.createElement('script');

          // 用 Blob URL 代替 inline script，避免 unsafe-inline 限制
          const wrapped = `
            (function() {
              var __result, __error;
              try {
                __result = eval(${JSON.stringify(code)});
              } catch(e) {
                __error = e.message;
              }
              window.${callbackId}({result: __result, error: __error});
            })();
          `;

          const blob = new Blob([wrapped], { type: 'text/javascript' });
          const url = URL.createObjectURL(blob);

          window[callbackId] = function(data) {
            delete window[callbackId];
            URL.revokeObjectURL(url);
            if (script.parentNode) script.parentNode.removeChild(script);
            if (data.error) {
              resolve('Error: ' + data.error);
            } else {
              resolve(String(data.result));
            }
          };

          script.src = url;
          script.onerror = function() {
            delete window[callbackId];
            URL.revokeObjectURL(url);
            resolve('Error: Script injection blocked (CSP)');
          };

          (document.head || document.documentElement).appendChild(script);
        } catch (e) {
          resolve('Error: ' + e.message);
        }
      });
    },
    args: [args.js]
  });

  // 结果可能是 Promise（返回了 promise），也可能直接是字符串
  const value = result.result;
  if (value && typeof value.then === 'function') {
    // 这个分支不应该发生，因为 executeScript 的 func 返回值中如果包含 Promise 会被展开
    // 但为了安全保留
    const awaited = await value;
    return { ok: true, result: awaited };
  }
  return { ok: true, result: value };
}

async function handleScreenshot(args) {
  const tabId = args.tab_id || await getActiveTabId();

  // Try real screenshot via captureVisibleTab first
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.id === tabId) {
      const dataUrl = await chrome.tabs.captureVisibleTab(null, { format: 'png' });
      return { ok: true, dataUrl, method: 'captureVisibleTab' };
    }
  } catch (e) {
    console.log('[CB] captureVisibleTab failed, falling back to canvas:', e.message);
  }

  // Fallback: make the target tab active and retry
  try {
    await chrome.tabs.update(tabId, { active: true });
    await new Promise(r => setTimeout(r, 300));
    const dataUrl = await chrome.tabs.captureVisibleTab(null, { format: 'png' });
    return { ok: true, dataUrl, method: 'captureVisibleTab (after activate)' };
  } catch (e) {
    console.log('[CB] captureVisibleTab retry failed, using canvas fallback:', e.message);
  }

  // Final fallback: canvas text rendering
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      try {
        const W = Math.min(window.innerWidth || 1280, 1920);
        const H = Math.min(window.innerHeight || 800, 2000);
        const c = document.createElement('canvas');
        c.width = W;
        c.height = H;
        const ctx = c.getContext('2d');

        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, W, H);

        ctx.fillStyle = '#f0f0f0';
        ctx.fillRect(0, 0, W, 50);
        ctx.fillStyle = '#1a1a1a';
        ctx.font = 'bold 16px Arial, sans-serif';
        const title = (document.title || 'Untitled').substring(0, 80);
        ctx.fillText(title, 16, 32);

        ctx.fillStyle = '#888';
        ctx.font = '11px Arial, sans-serif';
        const url = document.location.href.substring(0, 120);
        ctx.fillText(url, 16, 47);

        ctx.strokeStyle = '#ddd';
        ctx.beginPath();
        ctx.moveTo(0, 51);
        ctx.lineTo(W, 51);
        ctx.stroke();

        const body = document.body;
        if (body) {
          const clone = body.cloneNode(true);
          clone.querySelectorAll('script, style, noscript, svg, iframe, img, video, canvas, [aria-hidden="true"]').forEach(e => e.remove());
          const text = (clone.innerText || '').replace(/\n{3,}/g, '\n\n');
          const lines = text.split('\n');
          ctx.fillStyle = '#333';
          ctx.font = '12px "Courier New", monospace';
          let y = 72;
          const maxLines = Math.floor((H - 72) / 16);
          for (let i = 0; i < Math.min(lines.length, maxLines); i++) {
            const line = lines[i].substring(0, 160);
            if (line.trim()) {
              ctx.fillText(line, 12, y);
              y += 16;
            } else {
              y += 8;
            }
          }
          if (lines.length > maxLines) {
            ctx.fillStyle = '#999';
            ctx.fillText('...(truncated ' + (lines.length - maxLines) + ' lines)', 12, y);
          }
        }

        return c.toDataURL('image/png');
      } catch (e) {
        const c2 = document.createElement('canvas');
        c2.width = 600;
        c2.height = 100;
        const cx2 = c2.getContext('2d');
        cx2.fillStyle = '#fff';
        cx2.fillRect(0, 0, 600, 100);
        cx2.fillStyle = '#c00';
        cx2.font = '14px Arial';
        cx2.fillText('Screenshot error: ' + e.message, 10, 40);
        cx2.fillText('Page: ' + document.title, 10, 70);
        return c2.toDataURL('image/png');
      }
    }
  });

  return { ok: true, dataUrl: result.result, method: 'canvas-fallback' };
}

async function handleScroll(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const direction = args.direction || 'down'; // 'up', 'down', or 'top', 'bottom'
  const amount = args.amount || 500; // pixels

  await chrome.scripting.executeScript({
    target: { tabId },
    func: (dir, amt) => {
      switch (dir) {
        case 'top':
          window.scrollTo(0, 0);
          break;
        case 'bottom':
          window.scrollTo(0, document.body.scrollHeight);
          break;
        case 'up':
          window.scrollBy(0, -amt);
          break;
        case 'down':
        default:
          window.scrollBy(0, amt);
          break;
      }
      return { x: window.scrollX, y: window.scrollY };
    },
    args: [direction, amount]
  });
  return { ok: true };
}

async function handlePressKey(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const key = args.key || 'Enter';
  const selector = args.selector || null;
  const modifiers = args.modifiers || '';

  await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (keyName, sel, mods) => {
      let target = null;
      if (sel) {
        target = document.querySelector(sel);
        if (!target) throw new Error('Element not found: ' + sel);
        target.focus();
      } else {
        target = document.activeElement || document.body;
      }

      const keyMap = {
        'Enter':     { key: 'Enter',     code: 'Enter',     keyCode: 13 },
        'Tab':       { key: 'Tab',       code: 'Tab',       keyCode: 9 },
        'Escape':    { key: 'Escape',    code: 'Escape',    keyCode: 27 },
        'Backspace': { key: 'Backspace', code: 'Backspace', keyCode: 8 },
        'Space':     { key: ' ',         code: 'Space',     keyCode: 32 },
        'Delete':    { key: 'Delete',    code: 'Delete',    keyCode: 46 },
        'ArrowUp':   { key: 'ArrowUp',   code: 'ArrowUp',   keyCode: 38 },
        'ArrowDown': { key: 'ArrowDown', code: 'ArrowDown', keyCode: 40 },
        'ArrowLeft': { key: 'ArrowLeft', code: 'ArrowLeft', keyCode: 37 },
        'ArrowRight':{ key: 'ArrowRight',code: 'ArrowRight',keyCode: 39 },
        'PageUp':    { key: 'PageUp',    code: 'PageUp',    keyCode: 33 },
        'PageDown':  { key: 'PageDown',  code: 'PageDown',  keyCode: 34 },
        'Home':      { key: 'Home',      code: 'Home',      keyCode: 36 },
        'End':       { key: 'End',       code: 'End',       keyCode: 35 },
        'F1':  { key: 'F1',  code: 'F1',  keyCode: 112 },
        'F2':  { key: 'F2',  code: 'F2',  keyCode: 113 },
        'F3':  { key: 'F3',  code: 'F3',  keyCode: 114 },
        'F4':  { key: 'F4',  code: 'F4',  keyCode: 115 },
        'F5':  { key: 'F5',  code: 'F5',  keyCode: 116 },
        'F6':  { key: 'F6',  code: 'F6',  keyCode: 117 },
        'F7':  { key: 'F7',  code: 'F7',  keyCode: 118 },
        'F8':  { key: 'F8',  code: 'F8',  keyCode: 119 },
        'F9':  { key: 'F9',  code: 'F9',  keyCode: 120 },
        'F10': { key: 'F10', code: 'F10', keyCode: 121 },
        'F11': { key: 'F11', code: 'F11', keyCode: 122 },
        'F12': { key: 'F12', code: 'F12', keyCode: 123 },
      };
      const keyInfo = keyMap[keyName] || { key: keyName, code: keyName, keyCode: 0 };

      const modStr = (mods || '').toLowerCase();
      const modKeys = {
        ctrl: modStr.includes('ctrl'),
        alt: modStr.includes('alt'),
        shift: modStr.includes('shift'),
        meta: modStr.includes('meta'),
      };

      ['keydown', 'keypress', 'keyup'].forEach(type => {
        const event = new KeyboardEvent(type, {
          bubbles: true,
          cancelable: true,
          key: keyInfo.key,
          code: keyInfo.code,
          keyCode: keyInfo.keyCode,
          which: keyInfo.keyCode,
          ctrlKey: modKeys.ctrl,
          altKey: modKeys.alt,
          shiftKey: modKeys.shift,
          metaKey: modKeys.meta,
        });
        target.dispatchEvent(event);
      });
    },
    args: [key, selector, modifiers]
  });
  return { ok: true };
}

async function handleFindElement(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: (sel) => {
      const el = document.querySelector(sel);
      if (!el) return { found: false };
      const rect = el.getBoundingClientRect();
      return {
        found: true,
        tag: el.tagName,
        text: (el.textContent || '').trim().substring(0, 200),
        visible: rect.width > 0 && rect.height > 0,
        rect: { x: rect.x, y: rect.y, w: rect.width, h: rect.height }
      };
    },
    args: [args.selector]
  });
  return { ok: true, ...result.result };
}

async function handleFetchApi(args) {
  // Injects a fetch call into the page context (not eval-based, so no CSP issues)
  const tabId = args.tab_id || await getActiveTabId();
  const url = args.url;
  const body = args.body || '';
  const method = args.method || 'POST';
  const headers = args.headers || '{"Content-Type":"application/json"}';

  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: async (fetchUrl, fetchMethod, fetchBody, fetchHeaders) => {
      try {
        let parsedHeaders = { 'Content-Type': 'application/json' };
        try {
          parsedHeaders = JSON.parse(fetchHeaders);
        } catch(e) {}
        const opts = {
          method: fetchMethod,
          headers: parsedHeaders,
        };
        if (fetchBody) opts.body = fetchBody;
        const resp = await fetch(fetchUrl, opts);
        const text = await resp.text();
        // Return status and headers too
        const respHeaders = {};
        resp.headers.forEach((v, k) => { respHeaders[k] = v; });
        return JSON.stringify({ status: resp.status, headers: respHeaders, body: text });
      } catch (e) {
        return JSON.stringify({ error: e.message });
      }
    },
    args: [url, method, body, headers]
  });

  try {
    return { ok: true, data: JSON.parse(result.result) };
  } catch (e) {
    return { ok: true, result: result.result };
  }
}

async function handleTypeActive(args) {
  // Type text into whichever element currently has focus in the page
  const tabId = args.tab_id || await getActiveTabId();
  const text = args.text || '';

  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (txt) => {
      const el = document.activeElement;
      if (!el) return JSON.stringify({ error: 'No active element' });

      // Use native setter to bypass Vue
      const nativeSetter = Object.getOwnPropertyDescriptor(
        el.tagName === 'INPUT' || el.tagName === 'TEXTAREA'
          ? window.HTMLInputElement.prototype : window.HTMLTextAreaElement.prototype,
        'value'
      );
      const setter = nativeSetter ? nativeSetter.set : null;
      if (setter) {
        setter.call(el, txt);
      } else {
        el.value = txt;
        el.textContent = txt;
      }

      // Dispatch events to trigger Vue v-model
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
      el.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 'Unidentified' }));

      return JSON.stringify({
        success: true,
        tag: el.tagName,
        type: el.type || '',
        className: (el.className || '').substring(0, 60),
        placeholder: (el.placeholder || '').substring(0, 40),
        value: el.value ? el.value.substring(0, 30) : '',
      });
    },
    args: [text]
  });

  try {
    return { ok: true, data: JSON.parse(result.result) };
  } catch (e) {
    return { ok: true, raw: result.result };
  }
}



async function handleGetImages(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const maxWait = args.max_wait_ms || 15000;  // 最长等 15 秒
  const pollInterval = 1000;                   // 每秒检查一次
  const minLargeImgs = args.min_large || 1;   // 至少需要几张 >=400px 大图

  const startedAt = Date.now();
  let lastResult = null;

  while (true) {
    const [result] = await chrome.scripting.executeScript({
      target: { tabId },
      func: (minW, minH, needLarge) => {
        const imgs = document.querySelectorAll('img[src]');
        const data = [];
        let largeCount = 0;
        imgs.forEach(img => {
          const rect = img.getBoundingClientRect();
          if (rect.width > minW && rect.height > minH) {
            data.push({
              src: img.src,
              width: Math.round(rect.width),
              height: Math.round(rect.height),
              y: Math.round(rect.y),
              alt: (img.alt || '').substring(0, 40),
            });
            if (rect.width >= 400) largeCount++;
          }
        });
        data.sort((a, b) => a.y - b.y);
        return JSON.stringify({
          total: data.length,
          largeCount: largeCount,
          images: data.slice(0, 20),
          elapsed: 0  // placeholder, filled by caller
        });
      },
      args: [100, 100, minLargeImgs]
    });

    try {
      lastResult = JSON.parse(result.result);
    } catch(e) {
      return { ok: true, raw: result.result };
    }

    const elapsed = Date.now() - startedAt;

    // 成功条件：有大图，或已等到超时
    if (lastResult.largeCount >= minLargeImgs || elapsed >= maxWait) {
      lastResult.elapsed = elapsed;
      return { ok: true, data: lastResult, polled: true };
    }

    // 还没就绪，等一轮再检查
    await new Promise(r => setTimeout(r, pollInterval));
  }
}

async function handleWait(args) {
  const ms = args.ms || 1000;
  const tabId = args.tab_id || await getActiveTabId();
  await new Promise(r => setTimeout(r, ms));
  try {
    const tab = await chrome.tabs.get(tabId);
    return { ok: true, tabId, url: tab.url, title: tab.title };
  } catch (e) {
    return { ok: true, tabId, url: '(closed)', title: '(closed)' };
  }
}

async function handleTypeTrusted(args) {
  // 通过 CDP Input.insertText 发送可信键入事件，React 会正常响应
  const tabId = args.tab_id || await getActiveTabId();
  const selector = args.selector;
  const text = args.text || '';

  if (!selector) return { ok: false, error: 'selector is required' };

  try {
    // 1. 先通过 DOM 获取元素位置和 focus
    const [focusResult] = await chrome.scripting.executeScript({
      target: { tabId },
      world: 'MAIN',
      func: (sel) => {
        const el = document.querySelector(sel);
        if (!el) return JSON.stringify({ error: 'Element not found: ' + sel });
        el.focus();
        el.select();
        const rect = el.getBoundingClientRect();
        return JSON.stringify({
          found: true,
          tag: el.tagName,
          type: el.type || '',
          oldValue: el.value || '',
          x: Math.round(rect.x + rect.width / 2),
          y: Math.round(rect.y + rect.height / 2),
        });
      },
      args: [selector]
    });

    let info;
    try { info = JSON.parse(focusResult.result); } catch (e) {
      return { ok: false, error: 'Failed to parse focus result: ' + focusResult.result };
    }
    if (info.error) return { ok: false, error: info.error };

    // 2. 通过 CDP 可信事件键入新值
    try {
      await chrome.debugger.attach({ tabId }, '1.3');
    } catch (e) {
      // 可能已被 CSP bypass 或其他工具 attach，尝试继续
      console.log('[CB] debugger attach note:', e.message);
    }

    try {
      // 全选 (Ctrl+A)
      await chrome.debugger.sendCommand({ tabId }, 'Input.dispatchKeyEvent', {
        type: 'keyDown',
        modifiers: 2, // Ctrl
        windowsVirtualKeyCode: 65,
        key: 'a',
        code: 'KeyA',
      });

      // 用 insertText 一次性插入新文本
      await chrome.debugger.sendCommand({ tabId }, 'Input.insertText', {
        text: text,
      });

      // 确保 CSP bypass 保持生效
      try {
        await chrome.debugger.sendCommand({ tabId }, 'Page.setBypassCSP', { enabled: true });
      } catch (e) {}

      await chrome.debugger.detach({ tabId });
    } catch (cdpErr) {
      try { await chrome.debugger.detach({ tabId }); } catch (e) {}
      return { ok: false, error: 'CDP type failed: ' + cdpErr.message };
    }

    // 3. 验证结果
    const [verify] = await chrome.scripting.executeScript({
      target: { tabId },
      func: (sel) => {
        const el = document.querySelector(sel);
        return el ? el.value : null;
      },
      args: [selector]
    });

    return {
      ok: true,
      oldValue: info.oldValue,
      newValue: verify.result,
      typed: text,
    };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

async function handleFileChooserIntercept(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const filePaths = args.file_paths;
  const clickSelector = args.click_selector;

  if (!filePaths || (Array.isArray(filePaths) && filePaths.length === 0)) {
    return { ok: false, error: 'file_paths is required' };
  }

  const paths = Array.isArray(filePaths) ? filePaths : [filePaths];

  // 强制 detach 已有 debugger，确保干净状态
  try { await chrome.debugger.detach({ tabId }); } catch (e) {}

  try {
    await chrome.debugger.attach({ tabId }, '1.3');
  } catch (e) {
    return { ok: false, error: 'debugger attach failed: ' + e.message };
  }

  try {
    // 开启文件选择器拦截
    const interceptResult = await chrome.debugger.sendCommand(
      { tabId }, 'Page.setInterceptFileChooserDialog', { enabled: true }
    );
    console.log('[CB] file chooser intercept enabled:', JSON.stringify(interceptResult));

    // 维持 CSP 绕过
    try {
      await chrome.debugger.sendCommand({ tabId }, 'Page.setBypassCSP', { enabled: true });
    } catch (e) {}

    // If click_selector provided: click to trigger file chooser
    // If omitted: just listen — intercepts the next file chooser that opens on this tab
    if (clickSelector) {
      console.log('[CB] clicking via Blob URL injection:', clickSelector);
      const [clickResult] = await chrome.scripting.executeScript({
        target: { tabId },
        world: 'MAIN',
        func: (sel) => {
          return new Promise((resolve) => {
            const callbackId = '__cbfc_' + Math.random().toString(36).slice(2);
            const wrapped = `
              (function() {
                var el = document.querySelector('${sel.replace(/'/g, "\\'")}');
                if (!el) { window.${callbackId}(JSON.stringify({error:'Element not found: ${sel.replace(/'/g, "\\'")}'})); return; }
                el.scrollIntoView({ behavior: 'instant', block: 'center' });
                el.click();
                window.${callbackId}(JSON.stringify({ok:true}));
              })();
            `;
            const blob = new Blob([wrapped], { type: 'text/javascript' });
            const url = URL.createObjectURL(blob);

            window[callbackId] = function(data) {
              delete window[callbackId];
              URL.revokeObjectURL(url);
              if (script.parentNode) script.parentNode.removeChild(script);
              resolve(data);
            };

            const script = document.createElement('script');
            script.src = url;
            script.onerror = function() {
              delete window[callbackId];
              URL.revokeObjectURL(url);
              resolve(JSON.stringify({error: 'Script injection blocked'}));
            };
            (document.head || document.documentElement).appendChild(script);
          });
        },
        args: [clickSelector],
      });

      let clickInfo;
      try { clickInfo = JSON.parse(clickResult.result); } catch(e) { clickInfo = {raw: clickResult.result}; }
      console.log('[CB] click result:', JSON.stringify(clickInfo));
      if (clickInfo.error) {
        try { await chrome.debugger.detach({ tabId }); } catch (e) {}
        return { ok: false, error: 'Click failed: ' + clickInfo.error };
      }
      console.log('[CB] Blob URL click sent, waiting for file chooser...');
    } else {
      console.log('[CB] No click_selector provided — waiting for any file chooser on this tab...');
    }

    // 等待文件选择器事件
    return new Promise((resolve) => {
      const timeout = setTimeout(() => {
        chrome.debugger.onEvent.removeListener(handler);
        chrome.debugger.detach({ tabId }).catch(() => {});
        resolve({ ok: false, error: 'Timeout (30s) - file chooser did not open' });
      }, 30000);

      const handler = async (source, method, params) => {
        if (source.tabId === tabId && method === 'Page.fileChooserOpened') {
          clearTimeout(timeout);
          chrome.debugger.onEvent.removeListener(handler);
          console.log('[CB] file chooser opened, injecting files:', paths);

          try {
            await chrome.debugger.sendCommand({ tabId }, 'Page.handleFileChooser', {
              action: 'accept', files: paths,
            });
            chrome.debugger.detach({ tabId }).catch(() => {});
            resolve({ ok: true, action: 'accept', files: paths, tabId });
          } catch (e) {
            chrome.debugger.detach({ tabId }).catch(() => {});
            resolve({ ok: false, error: 'handleFileChooser failed: ' + e.message });
          }
        }
      };

      chrome.debugger.onEvent.addListener(handler);
    });
  } catch (e) {
    try { chrome.debugger.detach({ tabId }); } catch (e2) {}
    return { ok: false, error: 'Setup failed: ' + e.message };
  }
}

// ── Mouse ───────────────────────────────────────────────────────

async function handleHover(args) {
  const tabId = args.tab_id || await getActiveTabId();
  await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (sel) => {
      const el = document.querySelector(sel);
      if (!el) throw new Error('Element not found: ' + sel);
      el.scrollIntoView({ behavior: 'instant', block: 'center' });
      ['mouseover', 'mouseenter', 'mousemove'].forEach(type => {
        el.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window }));
      });
    },
    args: [args.selector]
  });
  return { ok: true };
}

async function handleDoubleClick(args) {
  const tabId = args.tab_id || await getActiveTabId();
  await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (sel) => {
      const el = document.querySelector(sel);
      if (!el) throw new Error('Element not found: ' + sel);
      el.scrollIntoView({ behavior: 'instant', block: 'center' });
      el.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: window }));
    },
    args: [args.selector]
  });
  return { ok: true };
}

async function handleRightClick(args) {
  const tabId = args.tab_id || await getActiveTabId();
  await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (sel) => {
      const el = document.querySelector(sel);
      if (!el) throw new Error('Element not found: ' + sel);
      el.scrollIntoView({ behavior: 'instant', block: 'center' });
      el.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, view: window, button: 2 }));
    },
    args: [args.selector]
  });
  return { ok: true };
}

// ── Form ────────────────────────────────────────────────────────

async function handleSelectOption(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const value = args.value || '';
  const text = args.text || '';
  const index = args.index;
  await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (sel, optValue, optText, optIndex) => {
      const el = document.querySelector(sel);
      if (!el) throw new Error('Element not found: ' + sel);
      if (el.tagName !== 'SELECT') throw new Error('Element is not a <select>: ' + el.tagName);

      let option = null;
      if (optIndex !== null && optIndex !== undefined) {
        option = el.options[optIndex];
      }
      if (!option && optValue) {
        option = el.querySelector(`option[value="${optValue.replace(/"/g, '\\"')}"]`);
      }
      if (!option && optText) {
        const options = el.querySelectorAll('option');
        for (const opt of options) {
          if (opt.textContent.trim() === optText || opt.textContent.trim().includes(optText)) {
            option = opt;
            break;
          }
        }
      }
      if (!option) throw new Error('Option not found');

      option.selected = true;
      el.dispatchEvent(new Event('change', { bubbles: true }));
      el.dispatchEvent(new Event('input', { bubbles: true }));
    },
    args: [args.selector, value, text, index]
  });
  return { ok: true };
}

// ── Navigation ──────────────────────────────────────────────────

async function handleGoBack(args) {
  const tabId = args.tab_id || await getActiveTabId();
  try {
    await chrome.tabs.goBack(tabId);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: 'Cannot go back: ' + e.message };
  }
}

async function handleGoForward(args) {
  const tabId = args.tab_id || await getActiveTabId();
  try {
    await chrome.tabs.goForward(tabId);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: 'Cannot go forward: ' + e.message };
  }
}

async function handleReload(args) {
  const tabId = args.tab_id || await getActiveTabId();
  await chrome.tabs.reload(tabId);
  return { ok: true };
}

// ── Content ─────────────────────────────────────────────────────

async function handleGetHtml(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => document.documentElement.outerHTML
  });
  return { ok: true, html: result.result };
}

async function handleGetAttribute(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const attribute = args.attribute || args.attr || '';
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: (sel, attr) => {
      const el = document.querySelector(sel);
      if (!el) return JSON.stringify({ error: 'Element not found: ' + sel });
      if (attr === 'innerHTML') return JSON.stringify({ value: el.innerHTML, found: true });
      if (attr === 'outerHTML') return JSON.stringify({ value: el.outerHTML, found: true });
      if (attr === 'textContent') return JSON.stringify({ value: el.textContent, found: true });
      if (attr === 'class') return JSON.stringify({ value: el.className, found: true });
      const val = el.getAttribute(attr);
      return JSON.stringify({ value: val, found: true });
    },
    args: [args.selector, attribute]
  });
  try { return { ok: true, ...JSON.parse(result.result) }; }
  catch(e) { return { ok: true, raw: result.result }; }
}

// ── Wait ────────────────────────────────────────────────────────

async function handleWaitForElement(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const selector = args.selector;
  if (!selector) return { ok: false, error: 'selector is required' };
  const timeout = Number(args.timeout) || 10000;
  const interval = Number(args.interval) || 300;

  const startedAt = Date.now();
  while (true) {
    const [result] = await chrome.scripting.executeScript({
      target: { tabId },
      func: (sel) => {
        const el = document.querySelector(sel);
        if (!el) return null;
        const rect = el.getBoundingClientRect();
        return { found: true, tag: el.tagName, text: (el.textContent || '').trim().substring(0, 100), visible: rect.width > 0 && rect.height > 0 };
      },
      args: [selector]
    });
    if (result.result) return { ok: true, ...result.result, elapsed: Date.now() - startedAt };
    if (Date.now() - startedAt >= timeout) return { ok: false, error: `Timeout (${timeout}ms) waiting for: ${selector}`, elapsed: Date.now() - startedAt };
    await new Promise(r => setTimeout(r, interval));
  }
}

// ── Dialogs ─────────────────────────────────────────────────────

async function handleDialog(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const action = args.action || 'dismiss'; // 'accept' or 'dismiss'
  const promptText = args.prompt_text || '';

  try { await chrome.debugger.attach({ tabId }, '1.3'); } catch(e) {}
  try { await chrome.debugger.sendCommand({ tabId }, 'Page.enable'); } catch(e) {}

  try {
    // First attempt: handle immediately if dialog is already open
    await chrome.debugger.sendCommand({ tabId }, 'Page.handleJavaScriptDialog', {
      accept: action === 'accept',
      promptText: action === 'accept' ? promptText : undefined,
    });
    await chrome.debugger.detach({ tabId }).catch(() => {});
    return { ok: true, action };
  } catch(e) {
    // No dialog yet — wait for one to appear
    try {
      const dialogResult = await new Promise((resolve) => {
        const timeout = setTimeout(() => {
          chrome.debugger.onEvent.removeListener(handler);
          chrome.debugger.detach({ tabId }).catch(() => {});
          resolve({ ok: false, error: 'Timeout (10s) — no dialog appeared' });
        }, 10000);

        const handler = async (source, method, params) => {
          if (source.tabId === tabId && method === 'Page.javascriptDialogOpening') {
            clearTimeout(timeout);
            chrome.debugger.onEvent.removeListener(handler);
            try {
              await chrome.debugger.sendCommand({ tabId }, 'Page.handleJavaScriptDialog', {
                accept: action === 'accept',
                promptText: action === 'accept' ? promptText : undefined,
              });
              await chrome.debugger.detach({ tabId }).catch(() => {});
              resolve({ ok: true, dialogType: params.type, message: params.message, action });
            } catch(err) {
              await chrome.debugger.detach({ tabId }).catch(() => {});
              resolve({ ok: false, error: err.message });
            }
          }
        };
        chrome.debugger.onEvent.addListener(handler);
      });
      return dialogResult;
    } catch(waitErr) {
      try { await chrome.debugger.detach({ tabId }); } catch(e2) {}
      return { ok: false, error: waitErr.message };
    }
  }
}

// ── Storage ─────────────────────────────────────────────────────

async function handleGetCookies(args) {
  const url = args.url || '';
  try {
    const cookies = await chrome.cookies.getAll(url ? { url } : {});
    return { ok: true, cookies };
  } catch(e) {
    return { ok: false, error: e.message };
  }
}

async function handleSetCookie(args) {
  const cookie = {
    url: args.url,
    name: args.name || '',
    value: args.value || '',
  };
  if (args.domain) cookie.domain = args.domain;
  if (args.path) cookie.path = args.path;
  if (args.secure) cookie.secure = true;
  if (args.httpOnly) cookie.httpOnly = true;
  if (args.expirationDate) cookie.expirationDate = Number(args.expirationDate);

  try {
    const result = await chrome.cookies.set(cookie);
    return { ok: true, cookie: result };
  } catch(e) {
    return { ok: false, error: e.message };
  }
}

async function handleGetStorage(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const key = args.key || null;
  const store = args.store || 'local'; // 'local' or 'session'
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (k, s) => {
      const storage = s === 'session' ? sessionStorage : localStorage;
      if (k) return JSON.stringify({ key: k, value: storage.getItem(k) });
      const items = {};
      for (let i = 0; i < storage.length; i++) {
        const keyName = storage.key(i);
        try { items[keyName] = storage.getItem(keyName); } catch(e) {}
      }
      return JSON.stringify(items);
    },
    args: [key, store]
  });
  try { return { ok: true, data: JSON.parse(result.result) }; }
  catch(e) { return { ok: true, raw: result.result }; }
}

async function handleSetStorage(args) {
  const tabId = args.tab_id || await getActiveTabId();
  const key = args.key || '';
  const value = args.value || '';
  const store = args.store || 'local';
  await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (k, v, s) => {
      const storage = s === 'session' ? sessionStorage : localStorage;
      storage.setItem(k, v);
    },
    args: [key, value, store]
  });
  return { ok: true };
}

// ==================== Helpers ====================

async function getActiveTabId() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) throw new Error('No active tab found');
  return tab.id;
}

// ==================== CSP Bypass ====================

chrome.runtime.onMessage.addListener(async (msg, sender) => {
  if (msg.action !== 'bypassCSP') return;

  const tabId = sender.tab?.id;
  if (!tabId) return;

  try {
    // attach → bypass → 立刻 detach（bypass 设置会保持）
    await chrome.debugger.attach({ tabId }, '1.3');
    await chrome.debugger.sendCommand({ tabId }, 'Page.setBypassCSP', { enabled: true });
    await chrome.debugger.detach({ tabId });
  } catch (e) {
    // 静默失败，不影响页面加载
  }
});

// ==================== Service Worker Keepalive ====================

// Use chrome.alarms for reliable keepalive (survives SW suspension)
chrome.alarms.create('keepalive', { periodInMinutes: 0.5 }); // every 30 seconds

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'keepalive') {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.log('[CB] Alarm: reconnecting...');
      connect();
    } else {
      // Send heartbeat ping
      try {
        ws.send(JSON.stringify({ id: 'hb_' + Date.now(), cmd: 'ping', args: {} }));
      } catch (e) {
        console.log('[CB] Heartbeat failed, reconnecting...');
        connect();
      }
    }
  }
});

// ==================== Action click (activates permissions) ====================

chrome.action.onClicked.addListener(() => {
  console.log('[CB] Extension icon clicked — permissions activated');
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    connect();
  }
});

// ==================== Startup ====================

chrome.runtime.onInstalled.addListener(() => {
  console.log('[CB] Extension installed/updated');
  // Ensure alarm is set after install/update
  chrome.alarms.create('keepalive', { periodInMinutes: 0.5 });
});

// Connect with a short delay to let the worker fully initialize
setTimeout(() => {
  console.log('[CB] Starting initial connection...');
  connect();
}, 100);
