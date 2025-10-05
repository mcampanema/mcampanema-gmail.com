/* tslint:disable */
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

// Add SpeechRecognition types to fix compilation errors
interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number;
  readonly results: SpeechRecognitionResultList;
}

interface SpeechRecognitionResultList {
  readonly length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  readonly isFinal: boolean;
  readonly length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
  readonly transcript: string;
  readonly confidence: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  readonly error: string;
  readonly message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: (event: SpeechRecognitionEvent) => void;
  onerror: (event: SpeechRecognitionErrorEvent) => void;
  onend: () => void;
  start(): void;
  stop(): void;
}

interface SpeechRecognitionStatic {
  new (): SpeechRecognition;
}

declare global {
  interface Window {
    SpeechRecognition: SpeechRecognitionStatic;
    webkitSpeechRecognition: SpeechRecognitionStatic;
    webkitAudioContext: typeof AudioContext;
  }
}

import {
  Content,
  GoogleGenAI,
  Chat,
  Part,
  File as GenAIFile,
  FileState,
} from '@google/genai';
import {LitElement, css, html, nothing} from 'lit';
import {customElement, state, query, property} from 'lit/decorators.js';
import './Visual3D.js';
import {getYouTubeVideoId} from './utils.js';
import {uploadFile} from './api.js';
import modes from './modes.js';

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

const SUPPORTED_MIME_TYPES = [
  'image/png',
  'image/jpeg',
  'image/webp',
  'image/heic',
  'image/heif',
  'video/mp4',
  'video/mpeg',
  'video/mov',
  'video/avi',
  'video/x-flv',
  'video/mpg',
  'video/webm',
  'video/wmv',
  'video/3gpp',
  'audio/wav',
  'audio/mp3',
  'audio/aiff',
  'audio/aac',
  'audio/ogg',
  'audio/flac',
  'application/pdf',
  'text/plain',
  'text/html',
  'text/css',
  'text/javascript',
  'application/x-javascript',
  'text/x-typescript',
  'application/x-typescript',
  'text/x-python',
  'application/x-python-code',
  'text/x-c',
  'text/x-csharp',
  'text/x-java',
  'application/json',
  'text/markdown',
];

const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

interface GroundingChunk {
  web: {
    uri: string;
    title: string;
  };
}

interface ManagedContent {
  role: 'user' | 'model';
  text: string;
  file?: {
    url?: string; // data URL for preview, optional on load
    name: string;
    type: string;
  };
  grounding?: GroundingChunk[];
  youtubeVideoId?: string | null;
  screenCaptures?: string[]; // array of dataUrls
  contextFilesUsed?: {name: string}[];
}

@customElement('live-chat')
export class LiveChat extends LitElement {
  @property({attribute: false})
  videoContextFile: {uri: string; mimeType: string} | null = null;

  @property({attribute: false})
  videoElement: HTMLVideoElement | null = null;

  @state() isRecording = false;
  @state() isProcessing = false;
  @state() status = 'Click the mic or type to talk';
  @state() error = '';
  @state() chatHistory: ManagedContent[] = [];
  @state() promptFile: File | null = null;
  @state() promptFilePreview: string | null = null;
  @state() isTtsEnabled = true;
  @state() private currentTranscript = '';
  @state() private textInputValue: string = '';
  @state() private isSharingScreen = false;
  @state() private screenCaptures: {dataUrl: string}[] = [];
  @state()
  private contextFiles: (GenAIFile & {isUploading?: boolean})[] = [];
  @state() private isVideoContextSent = false;

  @query('#chat-container') private chatContainer: HTMLDivElement;
  @query('#file-upload-input') private fileUploadInput: HTMLInputElement;
  @query('#history-upload-input') private historyUploadInput: HTMLInputElement;
  @query('#context-upload-input') private contextUploadInput: HTMLInputElement;
  @query('#text-input') private textInput: HTMLTextAreaElement;

  private client: GoogleGenAI;
  private chat: Chat;
  private recognition: SpeechRecognition;
  private screenStream: MediaStream | null = null;
  private screenShareVideoElement: HTMLVideoElement | null = null;

  private inputAudioContext = new (window.AudioContext ||
    window.webkitAudioContext)({sampleRate: 16000});
  @state() inputNode = this.inputAudioContext.createGain();

  private mediaStream?: MediaStream;
  private sourceNode?: MediaStreamAudioSourceNode;

  static styles = css`
    :host {
      font-family: 'Google Sans', sans-serif;
      --icon-button-size: 48px;
      display: flex;
      flex-direction: column;
      width: 100%;
      height: 100%;
      position: relative;
      overflow: hidden;
      background-color: #111;
    }

    #chat-container {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
      color: white;
      padding: 20px;
      scrollbar-width: thin;
      scrollbar-color: #6b7280 #1f2937;
    }

    .message {
      padding: 12px;
      border-radius: 12px;
      max-width: 80%;
      line-height: 1.5;
      animation: fadeIn 0.5s ease-in-out;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .message p {
      margin: 0;
      word-wrap: break-word;
    }

    .message img,
    .message video {
      max-width: 100%;
      border-radius: 8px;
    }

    .message .screen-captures-container {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .message .screen-captures-container img {
      max-width: 100px;
      border-radius: 4px;
    }

    .message .context-files-container {
      font-size: 0.8em;
      color: #9ca3af;
      border-top: 1px solid #6b7280;
      padding-top: 8px;
      margin-top: 4px;
    }

    .youtube-embed {
      position: relative;
      padding-bottom: 56.25%; /* 16:9 aspect ratio */
      height: 0;
      overflow: hidden;
      max-width: 100%;
      background: #000;
      border-radius: 8px;
    }

    .youtube-embed iframe {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      border: 0;
    }

    .file-placeholder {
      font-style: italic;
      font-size: 0.9em;
      color: #9ca3af;
      padding: 8px;
      background-color: rgba(0, 0, 0, 0.2);
      border-radius: 6px;
      border: 1px dashed #6b7280;
    }

    .user-message {
      background-color: #3b82f6;
      align-self: flex-end;
      border-bottom-right-radius: 2px;
    }

    .model-message {
      background-color: #4b5563;
      align-self: flex-start;
      border-bottom-left-radius: 2px;
    }

    .sources {
      border-top: 1px solid #6b7280;
      padding-top: 8px;
      font-size: 0.8rem;
    }
    .sources strong {
      color: #9ca3af;
    }
    .sources ul {
      margin: 4px 0 0;
      padding-left: 18px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .sources a {
      color: #a5b4fc;
      text-decoration: none;
    }
    .sources a:hover {
      text-decoration: underline;
    }

    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    #status-container {
      position: absolute;
      bottom: 160px;
      left: 0;
      right: 0;
      z-index: 10;
      text-align: center;
      color: #9ca3af;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      pointer-events: none;
    }

    #status,
    #live-transcript {
      color: white;
      margin-top: 8px;
      padding: 4px 12px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      max-width: 60vw;
      text-align: center;
    }

    #file-preview {
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.1);
      padding: 4px 8px;
      border-radius: 8px;
      pointer-events: auto;
    }

    #file-preview img {
      width: 32px;
      height: 32px;
      object-fit: cover;
      border-radius: 4px;
    }

    .file-icon-placeholder {
      width: 32px;
      height: 32px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #4b5563;
    }

    .file-icon-placeholder svg {
      width: 20px;
      height: 20px;
    }

    #file-preview span {
      font-size: 0.9em;
    }

    .controls {
      z-index: 10;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16px;
      padding: 10px 0;
      border-top: 1px solid #37393c;
    }

    .icon-button {
      outline: none;
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: white;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.1);
      width: var(--icon-button-size);
      height: var(--icon-button-size);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background-color: 0.2s;
      flex-shrink: 0;
    }

    .icon-button:hover:not(:disabled) {
      background: rgba(255, 255, 255, 0.2);
    }

    .icon-button:disabled {
      cursor: not-allowed;
      opacity: 0.5;
    }

    .talk-button {
      width: 80px;
      height: 80px;
      font-size: 24px;
    }

    .icon-button.recording,
    .talk-button.recording {
      background-color: #ef4444;
      animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
      0% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
      }
      70% {
        box-shadow: 0 0 0 20px rgba(239, 68, 68, 0);
      }
      100% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
      }
    }

    .hidden-input {
      display: none;
    }

    .chat-input-area {
      z-index: 10;
      padding-top: 8px;
      background-color: #111;
    }

    #text-input-container {
      display: flex;
      flex-direction: column;
      align-items: stretch;
      gap: 8px;
      padding: 10px 20px;
    }

    #previews-container {
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-height: 15vh;
      overflow-y: auto;
    }

    .context-files-list,
    .screen-captures-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-start;
    }

    .context-file-item,
    .screen-capture-item {
      background: rgba(255, 255, 255, 0.1);
      padding: 4px 8px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.9em;
      max-width: 250px;
    }

    .context-file-item.uploading {
      opacity: 0.6;
    }

    .screen-capture-item img {
      width: 48px;
      height: 48px;
      object-fit: cover;
      border-radius: 4px;
    }

    .context-file-item span {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .preview-remove-button {
      background: none;
      border: none;
      color: white;
      font-size: 20px;
      cursor: pointer;
      padding: 0;
      line-height: 1;
    }

    #text-input-row {
      display: flex;
      align-items: flex-end;
      gap: 8px;
    }

    #text-input {
      flex-grow: 1;
      background-color: #4b5563;
      border: 1px solid #6b7280;
      border-radius: 20px;
      padding: 10px 15px;
      color: white;
      font-family: 'Google Sans', sans-serif;
      font-size: 1rem;
      line-height: 1.5;
      resize: none;
      overflow-y: auto;
      max-height: 120px;
    }

    #text-input:focus {
      outline: none;
      border-color: #3b82f6;
    }

    #text-input:disabled {
      cursor: not-allowed;
      opacity: 0.5;
    }

    .send-button {
      width: 42px !important;
      height: 42px !important;
      border-radius: 50%;
      padding: 0;
      font-size: 20px;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .send-button svg {
      width: 24px;
      height: 24px;
    }

    .error {
      color: #f87171;
      background-color: #450a0a;
      padding: 8px 12px;
      border-radius: 8px;
      pointer-events: auto;
    }

    #file-preview button {
      background: none;
      border: none;
      color: white;
      font-size: 20px;
      cursor: pointer;
    }

    .prompt-starters {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 0 20px 12px;
    }

    .prompt-starter-button {
      background-color: #4b5563;
      color: white;
      border: none;
      border-radius: 16px;
      padding: 6px 12px;
      font-size: 0.9em;
      cursor: pointer;
      transition: background-color 0.2s;
    }

    .prompt-starter-button:hover:not(:disabled) {
      background-color: #6b7280;
    }

    .prompt-starter-button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  `;

  // Icons
  private readonly micIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>`;
  private readonly attachFileIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.59a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>`;
  private readonly sendIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`;
  private readonly speakerOnIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`;
  private readonly speakerOffIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="1" x2="1" y2="23"></line><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`;
  private readonly saveIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>`;
  private readonly loadIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>`;
  private readonly fileIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>`;
  private readonly addContextIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>`;
  private readonly screenShareIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="12" rx="2"/><line x1="12" y1="16" x2="12" y2="20"/><line x1="8" y1="20" x2="16" y2="20"/></svg>`;
  private readonly stopScreenShareIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="12" rx="2"/><line x1="12" y1="16" x2="12" y2="20"/><line x1="8" y1="20" x2="16" y2="20"/><line x1="2" y1="2" x2="22" y2="22"/></svg>`;
  private readonly captureIcon = html`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>`;

  constructor() {
    super();
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this._initializeRecognition();
    }
  }

  connectedCallback() {
    super.connectedCallback();
    try {
      if (!process.env.API_KEY) {
        throw new Error('API Key not found. Please set it.');
      }
      this.client = new GoogleGenAI({apiKey: process.env.API_KEY});
      this.chat = this.client.chats.create({model: 'gemini-2.5-flash'});
    } catch (e) {
      this.error = (e as Error).message;
      console.error(e);
    }
  }

  private _initializeRecognition() {
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';

    this.recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interimTranscript = '';
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }
      this.currentTranscript = finalTranscript + interimTranscript;
      if (finalTranscript) {
        this.textInputValue = (this.textInputValue + ' ' + finalTranscript).trim();
        this.currentTranscript = '';
      }
    };

    this.recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      this.error = `Speech recognition error: ${event.error}`;
      this.isRecording = false;
      this.status = 'Click the mic or type to talk';
    };

    this.recognition.onend = () => {
      if (this.isRecording) {
        // If it stops unexpectedly, restart it
        this.recognition.start();
      }
    };
  }

  async _toggleRecording() {
    if (!SpeechRecognition) {
      this.error = 'Speech recognition is not supported in this browser.';
      return;
    }
    this.isRecording = !this.isRecording;
    if (this.isRecording) {
      try {
        if (!this.mediaStream) {
          this.mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: true,
          });
          this.sourceNode =
            this.inputAudioContext.createMediaStreamSource(this.mediaStream);
          this.sourceNode.connect(this.inputNode);
        }
        this.recognition.start();
        this.status = 'Listening...';
        this.error = '';
        this.currentTranscript = '';
      } catch (e) {
        this.error =
          'Could not start recording. Please grant microphone permission.';
        this.isRecording = false;
        this.status = 'Click the mic or type to talk';
      }
    } else {
      this.recognition.stop();
      this.status = 'Click the mic or type to talk';
      if (this.textInputValue) {
        this._sendMessage();
      }
    }
  }

  private async _toggleScreenShare() {
    if (this.isSharingScreen) {
      this.screenStream?.getTracks().forEach((track) => track.stop());
      this.screenStream = null;
      this.screenShareVideoElement = null;
      this.isSharingScreen = false;
      this.status = 'Screen sharing stopped.';
      this._clearScreenCaptures();
    } else {
      try {
        this.screenStream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
        });
        this.isSharingScreen = true;
        this.status =
          'Screen sharing started. Use the capture button to take screenshots.';

        const videoEl = document.createElement('video');
        videoEl.autoplay = true;
        videoEl.muted = true;
        videoEl.srcObject = this.screenStream;
        await videoEl.play();
        this.screenShareVideoElement = videoEl;

        this.screenStream.getVideoTracks()[0].onended = () => {
          this.isSharingScreen = false;
          this.screenStream = null;
          this.screenShareVideoElement = null;
          this.status = 'Screen sharing stopped.';
          this._clearScreenCaptures();
        };
      } catch (err) {
        console.error('Error starting screen share:', err);
        this.error = 'Could not start screen sharing.';
        this.isSharingScreen = false;
      }
    }
  }

  private async _captureAndAddScreenFrame() {
    if (!this.screenShareVideoElement) {
      this.error = 'Screen sharing is not active or not ready.';
      return;
    }

    try {
      const canvas = document.createElement('canvas');
      if (
        this.screenShareVideoElement.readyState <
        this.screenShareVideoElement.HAVE_METADATA
      ) {
        await new Promise(
          (resolve) =>
            (this.screenShareVideoElement!.onloadedmetadata = resolve),
        );
      }
      canvas.width = this.screenShareVideoElement.videoWidth;
      canvas.height = this.screenShareVideoElement.videoHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.drawImage(
        this.screenShareVideoElement,
        0,
        0,
        canvas.width,
        canvas.height,
      );
      const dataUrl = canvas.toDataURL('image/jpeg');
      this.screenCaptures = [...this.screenCaptures, {dataUrl}];
    } catch (e) {
      this.error = `Could not capture screen frame: ${(e as Error).message}`;
    }
  }

  private _removeScreenCapture(index: number) {
    this.screenCaptures = this.screenCaptures.filter((_, i) => i !== index);
  }

  private _clearScreenCaptures() {
    this.screenCaptures = [];
  }

  private async _sendMessageWithRetry(parts: Part[], config: any) {
    let retries = 3;
    let delay = 1000; // Initial delay in ms
    let lastError: Error | null = null;

    while (retries > 0) {
      try {
        const response = await this.chat.sendMessage({
          message: parts,
          config: config,
        });
        return response; // Success!
      } catch (e) {
        lastError = e as Error;
        const errorMessage = lastError.message.toLowerCase();
        const isRateLimit =
          errorMessage.includes('429') ||
          errorMessage.includes('resource_exhausted');
        const isServerError =
          errorMessage.includes('500') || errorMessage.includes('internal');

        // Retry on rate limit or internal server errors
        if (isRateLimit || isServerError) {
          retries--;
          if (retries > 0) {
            const retryReason = isRateLimit ? 'Rate limit hit' : 'Server error';
            this.status = `${retryReason}. Retrying in ${delay / 1000}s...`;
            await new Promise((resolve) => setTimeout(resolve, delay));
            delay *= 2; // Exponential backoff
          }
        } else {
          // Not a retriable error, fail fast
          throw lastError;
        }
      }
    }
    // If all retries failed, throw a new, more user-friendly error.
    const finalErrorReason = lastError?.message.toLowerCase().includes('429')
      ? 'API rate limit exceeded'
      : 'A server error occurred';
    throw new Error(
      `${finalErrorReason} after multiple retries. Please try again later. Original error: ${lastError?.message}`,
    );
  }

  private async _processPrompt(promptText: string, file?: File) {
    this.isProcessing = true;
    this.status = 'Thinking...';
    this.error = '';

    const youTubeVideoId = getYouTubeVideoId(promptText);

    // --- Prepare the request for the Gemini API ---
    const parts: Part[] = [];
    let apiText = promptText;
    let filePreview: ManagedContent['file'] | undefined;
    let sentVideoContext = false;

    // Take a snapshot of the files/captures for this message
    const screenCapturesForMessage = [...this.screenCaptures];
    const activeContextFiles = this.contextFiles.filter((f) => !f.isUploading);

    // Add screen captures
    if (screenCapturesForMessage.length > 0) {
      for (const capture of screenCapturesForMessage) {
        const base64Data = capture.dataUrl.split(',')[1];
        parts.push({
          inlineData: {
            data: base64Data,
            mimeType: 'image/jpeg',
          },
        });
      }
    }

    // Add context files
    let contextPrompt = '';
    if (activeContextFiles.length > 0) {
      for (const contextFile of activeContextFiles) {
        parts.push({
          fileData: {
            mimeType: contextFile.mimeType,
            fileUri: contextFile.uri,
          },
        });
      }
      contextPrompt = `Using the provided file(s) (${activeContextFiles
        .map((f) => f.displayName)
        .join(', ')}) as context, `;
    }

    // Add context from video analyzer
    if (this.videoContextFile && !this.isVideoContextSent) {
      parts.push({
        fileData: {
          mimeType: this.videoContextFile.mimeType,
          fileUri: this.videoContextFile.uri,
        },
      });
      apiText = `Using the provided video as context, ${apiText}`;
      sentVideoContext = true;
    }

    // Add file uploaded in chat
    if (file) {
      try {
        const filePart = await this._fileToGenerativePart(file);
        parts.push(filePart);
        filePreview = {
          url: URL.createObjectURL(file), // Create URL for optimistic preview
          name: file.name,
          type: file.type,
        };
      } catch (e) {
        this.error = `Error processing file: ${(e as Error).message}`;
        this.isProcessing = false;
        this.status = 'Click the mic or type to talk';
        throw e; // Propagate error up to _sendMessage
      }
    }

    // Add user message to UI history first for responsiveness.
    const userMessage: ManagedContent = {
      role: 'user',
      text: promptText,
      file: filePreview,
      youtubeVideoId: youTubeVideoId,
      screenCaptures: screenCapturesForMessage.map((c) => c.dataUrl),
      contextFilesUsed: activeContextFiles.map((f) => ({
        name: f.displayName || 'file',
      })),
    };
    this.chatHistory = [...this.chatHistory, userMessage];

    const useSearch =
      !youTubeVideoId && parts.length === activeContextFiles.length;

    if (youTubeVideoId) {
      apiText = `Please analyze this youtube video and answer my questions. The video is at this URL: ${promptText}`;
    }

    if (parts.length > 0 && !apiText.trim()) {
      apiText = 'Describe the provided file(s).';
    }
    parts.unshift({text: `${contextPrompt}${apiText}`});

    const config: any = {};
    if (useSearch) {
      config.tools = [{googleSearch: {}}];
    }

    try {
      const response = await this._sendMessageWithRetry(parts, config);

      // ---- SUCCESS ----
      const text = response.text;
      const grounding =
        (response.candidates?.[0]?.groundingMetadata
          ?.groundingChunks as GroundingChunk[]) || [];

      this.chatHistory = [
        ...this.chatHistory,
        {role: 'model', text, grounding},
      ];
      if (sentVideoContext) {
        this.isVideoContextSent = true;
      }

      // Clear inputs now that we've successfully sent
      this._clearFile();
      this._clearScreenCaptures();

      if (this.isTtsEnabled) {
        await this._speak(text);
      }
    } catch (e) {
      // ---- FAILURE ----
      console.error(e);
      const errorMessage = (e as Error).message;
      if (
        errorMessage
          .toLowerCase()
          .includes('exceeds the maximum number of tokens allowed')
      ) {
        this.error =
          'Your request is too long. Please reduce text length, remove some files/captures, or start a new chat to reduce history size.';
      } else if (errorMessage.toLowerCase().includes('api key not valid')) {
        this.error = 'The API key is invalid. Please check your configuration.';
      } else {
        this.error = errorMessage;
      }

      // Remove the user message from history since it failed
      this.chatHistory = this.chatHistory.slice(0, -1);

      throw e; // Propagate error so _sendMessage knows not to clear text input
    } finally {
      this.isProcessing = false;
      this.status = 'Click the mic or type to talk';
      if (filePreview?.url) {
        // Always clean up the object URL
        URL.revokeObjectURL(filePreview.url);
      }
    }
  }

  private async _sendMessage() {
    const text = this.textInputValue.trim();
    if (!text && !this.promptFile && this.screenCaptures.length === 0) return;

    try {
      await this._processPrompt(text, this.promptFile ?? undefined);

      // It succeeded, so clear the text input.
      // File/capture inputs were cleared inside _processPrompt.
      this.textInputValue = '';
      if (this.textInput) {
        this.textInput.value = '';
        this.textInput.style.height = 'auto';
      }
    } catch (e) {
      // Error was already handled and displayed by _processPrompt.
      // We just catch it here to prevent it from bubbling up further
      // and to avoid clearing the text input.
      console.log('Send message failed, text input preserved.');
    }
  }

  private _handleTextInput(e: Event) {
    const textarea = e.target as HTMLTextAreaElement;
    this.textInputValue = textarea.value;
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  private _handleTextKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this._sendMessage();
    }
  }

  private _validateFile(file: File): boolean {
    if (!SUPPORTED_MIME_TYPES.includes(file.type)) {
      this.error = `Unsupported file type: '${
        file.type || 'unknown'
      }'. Please select a supported file.`;
      setTimeout(() => {
        if (this.error.startsWith('Unsupported file type')) this.error = '';
      }, 5000);
      return false;
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      this.error = `File is too large. Maximum size is ${MAX_FILE_SIZE_MB}MB.`;
      setTimeout(() => {
        if (this.error.includes('too large')) this.error = '';
      }, 5000);
      return false;
    }
    return true;
  }

  private async _handleFileUpload(e: Event) {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
      if (!this._validateFile(file)) {
        target.value = '';
        return;
      }
      this.promptFile = file;
      this.promptFilePreview = URL.createObjectURL(file);
      this.error = '';
    }
  }

  private async _handleContextFileUpload(e: Event) {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file) return;

    if (!this._validateFile(file)) {
      target.value = '';
      return;
    }

    const tempId = Date.now().toString();
    const placeholder: GenAIFile & {isUploading?: boolean} = {
      name: tempId,
      displayName: file.name,
      mimeType: file.type,
      uri: '',
      createTime: new Date().toISOString(),
      updateTime: new Date().toISOString(),
      expirationTime: '',
      sizeBytes: file.size.toString(),
      sha256Hash: '',
      // Fix: Use the `FileState` enum for type safety instead of a raw string.
      state: FileState.PROCESSING,
      isUploading: true,
    };
    this.contextFiles = [...this.contextFiles, placeholder];
    target.value = '';

    try {
      const uploadedFile = await uploadFile(file);
      this.contextFiles = this.contextFiles.map((f) =>
        f.name === tempId ? uploadedFile : f,
      );
    } catch (err) {
      this.error = `Failed to upload context file: ${(err as Error).message}`;
      this.contextFiles = this.contextFiles.filter((f) => f.name !== tempId);
    }
  }

  private _removeContextFile(index: number) {
    this.contextFiles = this.contextFiles.filter((_, i) => i !== index);
  }

  private _handleHistoryUpload(e: Event) {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file) {
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const content = event.target?.result as string;
        const loadedData = JSON.parse(content);

        if (!Array.isArray(loadedData)) {
          throw new Error('Invalid history file format: not an array.');
        }

        // Filter and type guard to ensure conformance with ManagedContent
        const validHistory: ManagedContent[] = loadedData.filter(
          (msg: any): msg is ManagedContent => {
            return (
              (msg.role === 'user' || msg.role === 'model') &&
              typeof msg.text === 'string'
            );
          },
        );

        this.chatHistory = validHistory;

        const geminiHistory: Content[] = validHistory.map((msg) => ({
          role: msg.role,
          parts: [{text: msg.text}],
        }));

        this.chat = this.client.chats.create({
          model: 'gemini-2.5-flash',
          history: geminiHistory,
        });

        this.error = '';
        this.status = 'Chat history loaded successfully.';
      } catch (err) {
        this.error = `Failed to load history: ${(err as Error).message}`;
      } finally {
        target.value = '';
      }
    };
    reader.onerror = () => {
      this.error = 'Failed to read the history file.';
      target.value = '';
    };
    reader.readAsText(file);
  }

  private _clearFile() {
    if (this.promptFilePreview) {
      URL.revokeObjectURL(this.promptFilePreview);
    }
    this.promptFile = null;
    this.promptFilePreview = null;
    if (this.fileUploadInput) this.fileUploadInput.value = '';
  }

  private async _fileToGenerativePart(file: File): Promise<Part> {
    const base64EncodedDataPromise = new Promise<string>((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () =>
        resolve((reader.result as string).split(',')[1]);
      reader.readAsDataURL(file);
    });
    return {
      inlineData: {
        data: await base64EncodedDataPromise,
        mimeType: file.type,
      },
    };
  }

  private async _speak(text: string) {
    if (
      !this.isTtsEnabled ||
      !('speechSynthesis' in window) ||
      !text?.trim()
    ) {
      return;
    }

    const getVoices = (): Promise<SpeechSynthesisVoice[]> => {
      return new Promise((resolve) => {
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
          resolve(voices);
          return;
        }
        window.speechSynthesis.onvoiceschanged = () => {
          resolve(window.speechSynthesis.getVoices());
        };
      });
    };

    try {
      // Cancel any previously queued speech. This is important for responsiveness.
      window.speechSynthesis.cancel();

      const voices = await getVoices();
      const englishVoice =
        voices.find(
          (voice) =>
            voice.lang.startsWith('en-') && voice.name.includes('Google'),
        ) ||
        voices.find((voice) => voice.lang.startsWith('en-')) ||
        voices.find((voice) => voice.default);

      const chunks: string[] = [];
      const MAX_CHUNK_LENGTH = 160; // Conservative chunk length to avoid TTS engine errors

      // 1. Split text into sentences to preserve natural pauses.
      const sentences = text.match(/[^.!?]+[.!?\s]*|[^.!?]+$/g) || [];

      // 2. For each sentence, if it's too long, split it further into smaller chunks by words.
      sentences.forEach((sentence) => {
        const trimmedSentence = sentence.trim();
        if (trimmedSentence.length === 0) return;

        if (trimmedSentence.length > MAX_CHUNK_LENGTH) {
          const words = trimmedSentence.split(/\s+/);
          let currentChunk = '';
          for (const word of words) {
            if (currentChunk.length + word.length + 1 > MAX_CHUNK_LENGTH) {
              chunks.push(currentChunk);
              currentChunk = word;
            } else {
              currentChunk += (currentChunk ? ' ' : '') + word;
            }
          }
          if (currentChunk) {
            chunks.push(currentChunk);
          }
        } else {
          chunks.push(trimmedSentence);
        }
      });

      // 3. Queue each chunk for speaking.
      for (const chunk of chunks) {
        if (!chunk) continue;
        const utterance = new SpeechSynthesisUtterance(chunk);

        if (englishVoice) {
          utterance.voice = englishVoice;
        }

        utterance.onerror = (event: SpeechSynthesisErrorEvent) => {
          // 'canceled' and 'interrupted' are expected if user actions stop speech. Not true errors.
          if (event.error === 'canceled' || event.error === 'interrupted') {
            return;
          }
          console.error(`SpeechSynthesis error: ${event.error}`, event);
          this.error = `Text-to-speech error: ${event.error}`;
        };

        window.speechSynthesis.speak(utterance);
      }
    } catch (e) {
      this.error = `Failed to initialize text-to-speech: ${
        (e as Error).message
      }`;
      console.error(e);
    }
  }

  private _toggleTts() {
    this.isTtsEnabled = !this.isTtsEnabled;
    if (!this.isTtsEnabled) {
      window.speechSynthesis.cancel();
    }
  }

  private _saveChat() {
    if (this.chatHistory.length === 0) {
      this.error = 'There is no chat history to save.';
      setTimeout(() => {
        if (this.error === 'There is no chat history to save.') this.error = '';
      }, 3000);
      return;
    }

    this.error = '';

    const serializableHistory = this.chatHistory.map((message) => ({
      role: message.role,
      text: message.text,
      grounding: message.grounding,
      file: message.file
        ? {name: message.file.name, type: message.file.type}
        : undefined,
    }));

    const historyJson = JSON.stringify(serializableHistory, null, 2);
    const blob = new Blob([historyJson], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `gemini-chat-history-${new Date()
      .toISOString()
      .slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  updated(changedProperties: Map<string, unknown>) {
    if (changedProperties.has('chatHistory')) {
      this._updateChatScroll();
    }
    if (changedProperties.has('textInputValue')) {
      if (this.textInput) {
        this.textInput.value = this.textInputValue;
      }
    }
    if (changedProperties.has('videoContextFile')) {
      if (this.videoContextFile) {
        // New video context. Reset chat.
        this.chat = this.client.chats.create({model: 'gemini-2.5-flash'});
        this.chatHistory = []; // Also clears UI
        this.isVideoContextSent = false;
      }
    }
  }

  private _updateChatScroll() {
    if (this.chatContainer) {
      setTimeout(() => {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
      }, 0);
    }
  }

  private _handlePromptStarterClick(prompt: string) {
    if (this.isProcessing) return;
    this.textInputValue = prompt;
    this.requestUpdate();
    this._sendMessage();
  }

  private renderPromptStarters() {
    if (!this.videoContextFile) {
      return nothing;
    }
    // Exclude modes that require custom input
    const simpleModes = Object.entries(modes).filter(
      ([key]) => key !== 'Chart' && key !== 'Custom',
    );

    return html`
      <div class="prompt-starters">
        ${simpleModes.map(
          ([key, value]) => html`
            <button
              class="prompt-starter-button"
              @click=${() =>
                this._handlePromptStarterClick(value.prompt as string)}
              ?disabled=${this.isProcessing}
              title=${value.prompt as string}>
              ${value.emoji} ${key}
            </button>
          `,
        )}
      </div>
    `;
  }

  private renderMessage(message: ManagedContent) {
    const isUser = message.role === 'user';
    const textWithBreaks = message.text.replace(/\n/g, '<br>');

    return html`
      <div class="message ${isUser ? 'user-message' : 'model-message'}">
        ${message.youtubeVideoId
          ? html`
              <div class="youtube-embed">
                <iframe
                  src="https://www.youtube.com/embed/${message.youtubeVideoId}"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen></iframe>
              </div>
            `
          : nothing}
        ${message.screenCaptures && message.screenCaptures.length > 0
          ? html`
              <div class="screen-captures-container">
                ${message.screenCaptures.map(
                  (dataUrl) => html`<img src=${dataUrl} alt="Screen capture" />`,
                )}
              </div>
            `
          : nothing}
        ${message.file
          ? html`
              ${message.file.url && message.file.type.startsWith('image/')
                ? html` <img src=${message.file.url} alt=${message.file.name} /> `
                : message.file.url && message.file.type.startsWith('video/')
                  ? html` <video src=${message.file.url} controls></video> `
                  : html`
                      <div class="file-placeholder">
                        File: ${message.file.name}
                      </div>
                    `}
            `
          : nothing}
        <p .innerHTML=${textWithBreaks}></p>
        ${message.contextFilesUsed && message.contextFilesUsed.length > 0
          ? html`<div class="context-files-container">
              Used context: ${message.contextFilesUsed.map((f) => f.name).join(', ')}
            </div>`
          : nothing}
        ${message.grounding && message.grounding.length > 0
          ? html`
              <div class="sources">
                <strong>Sources:</strong>
                <ul>
                  ${message.grounding.map(
                    (source) => html`<li>
                      <a
                        href=${source.web.uri}
                        target="_blank"
                        rel="noopener noreferrer"
                        >${source.web.title}</a
                      >
                    </li>`,
                  )}
                </ul>
              </div>
            `
          : nothing}
      </div>
    `;
  }

  render() {
    // Fix: Explicitly coerce `this.textInputValue` to a string to prevent a type error where it could be inferred as `never`.
    const isTextInputEmpty = String(this.textInputValue || '').trim() === '';
    const hasContentToSend =
      !isTextInputEmpty ||
      !!this.promptFile ||
      this.screenCaptures.length > 0;

    return html`
      <live-chat-visuals-3d
        .inputNode=${this.inputNode}
        .videoElement=${this.videoElement}></live-chat-visuals-3d>

      <div id="chat-container">
        ${this.chatHistory.map((message) => this.renderMessage(message))}
        ${this.videoContextFile && this.chatHistory.length === 0
          ? html`<div class="message model-message">
              <p>Video context loaded. Ask me anything about the video!</p>
            </div>`
          : nothing}
      </div>

      <div id="status-container">
        ${this.error ? html`<div class="error">${this.error}</div>` : nothing}
        ${this.isProcessing
          ? html`<div id="status">${this.status}</div>`
          : nothing}
        ${!this.isProcessing && this.isRecording && this.currentTranscript
          ? html`<div id="live-transcript">${this.currentTranscript}</div>`
          : nothing}
        ${!this.isProcessing && this.promptFilePreview
          ? html`
              <div id="file-preview">
                ${this.promptFile?.type.startsWith('image/')
                  ? html`<img src=${this.promptFilePreview} alt="File preview" />`
                  : html`<div class="file-icon-placeholder">
                      ${this.fileIcon}
                    </div>`}
                <span>${this.promptFile?.name}</span>
                <button @click=${this._clearFile} aria-label="Remove file">
                  &times;
                </button>
              </div>
            `
          : nothing}
      </div>

      <div class="chat-input-area">
        ${this.renderPromptStarters()}
        <div id="text-input-container">
          <div id="previews-container">
            ${this.contextFiles.length > 0
              ? html` <div class="context-files-list">
                  ${this.contextFiles.map(
                    (file, index) => html`
                      <div
                        class="context-file-item ${file.isUploading
                          ? 'uploading'
                          : ''}">
                        <span>${file.displayName}</span>
                        <button
                          class="preview-remove-button"
                          @click=${() => this._removeContextFile(index)}
                          aria-label="Remove context file">
                          &times;
                        </button>
                      </div>
                    `,
                  )}
                </div>`
              : nothing}
            ${this.screenCaptures.length > 0
              ? html`<div class="screen-captures-list">
                  ${this.screenCaptures.map(
                    (capture, index) => html`
                      <div class="screen-capture-item">
                        <img src=${capture.dataUrl} alt="Screen capture" />
                        <button
                          class="preview-remove-button"
                          @click=${() => this._removeScreenCapture(index)}
                          aria-label="Remove screen capture">
                          &times;
                        </button>
                      </div>
                    `,
                  )}
                </div>`
              : nothing}
          </div>
          <div id="text-input-row">
            <textarea
              id="text-input"
              placeholder="Type your message or paste a YouTube URL..."
              .value=${this.textInputValue}
              @input=${this._handleTextInput}
              @keydown=${this._handleTextKeydown}
              ?disabled=${this.isProcessing}
              rows="1"></textarea>
            <button
              class="icon-button send-button"
              @click=${this._sendMessage}
              ?disabled=${this.isProcessing || !hasContentToSend}>
              ${this.sendIcon}
            </button>
          </div>
        </div>
      </div>
      <div class="controls">
        <button
          class="icon-button"
          @click=${() => this.historyUploadInput.click()}
          title="Load Chat History"
          ?disabled=${this.isProcessing}>
          ${this.loadIcon}
        </button>
        <input
          type="file"
          id="history-upload-input"
          class="hidden-input"
          accept=".json"
          @change=${this._handleHistoryUpload} />

        <button
          class="icon-button"
          @click=${() => this.fileUploadInput.click()}
          title="Attach File"
          ?disabled=${this.isProcessing || !!this.promptFile}>
          ${this.attachFileIcon}
        </button>
        <input
          type="file"
          id="file-upload-input"
          class="hidden-input"
          @change=${this._handleFileUpload}
          accept=${SUPPORTED_MIME_TYPES.join(',')} />

        <button
          class="icon-button"
          @click=${() => this.contextUploadInput.click()}
          title="Add Context File"
          ?disabled=${this.isProcessing}>
          ${this.addContextIcon}
        </button>
        <input
          type="file"
          id="context-upload-input"
          class="hidden-input"
          @change=${this._handleContextFileUpload}
          accept=".txt,.json,.md,text/plain,application/json,text/markdown" />

        <button
          class="icon-button ${this.isSharingScreen ? 'recording' : ''}"
          @click=${this._toggleScreenShare}
          title=${this.isSharingScreen
            ? 'Stop Sharing'
            : 'Share Screen & Capture'}
          ?disabled=${this.isProcessing}>
          ${this.isSharingScreen
            ? this.stopScreenShareIcon
            : this.screenShareIcon}
        </button>

        ${this.isSharingScreen
          ? html` <button
              class="icon-button"
              @click=${this._captureAndAddScreenFrame}
              title="Capture Screen"
              ?disabled=${this.isProcessing}>
              ${this.captureIcon}
            </button>`
          : nothing}

        <button
          class="icon-button talk-button ${this.isRecording ? 'recording' : ''}"
          @click=${this._toggleRecording}
          ?disabled=${this.isProcessing}
          aria-label=${this.isRecording
            ? 'Stop Recording'
            : 'Start Recording'}>
          ${this.micIcon}
        </button>

        <button
          class="icon-button"
          @click=${this._toggleTts}
          title=${this.isTtsEnabled
            ? 'Disable Text-to-Speech'
            : 'Enable Text-to-Speech'}>
          ${this.isTtsEnabled ? this.speakerOnIcon : this.speakerOffIcon}
        </button>

        <button
          class="icon-button"
          @click=${this._saveChat}
          title="Save Chat History"
          ?disabled=${this.isProcessing || this.chatHistory.length === 0}>
          ${this.saveIcon}
        </button>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'live-chat': LiveChat;
  }
}