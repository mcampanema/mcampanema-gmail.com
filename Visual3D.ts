// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import {LitElement, css, html} from 'lit';
import {customElement, property} from 'lit/decorators.js';

@customElement('live-chat-visuals-3d')
export class Visual3D extends LitElement {
  @property({attribute: false})
  inputNode?: GainNode;

  @property({attribute: false})
  videoElement?: HTMLVideoElement;

  private analyser?: AnalyserNode;
  private dataArray?: Uint8Array;
  private canvasCtx?: CanvasRenderingContext2D;
  private canvasRef?: HTMLCanvasElement;
  private animationFrameId?: number;
  private sourceCleanup: (() => void) | null = null;

  static styles = css`
    :host {
      display: block;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: -1;
      opacity: 0.5;
    }
    canvas {
      width: 100%;
      height: 100%;
      background-color: #111;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    if (!this.animationFrameId) {
      this.draw();
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = undefined;
    }
    this.sourceCleanup?.();
    this.sourceCleanup = null;
  }

  firstUpdated() {
    // Fix: Use this.renderRoot which is a correctly typed property on LitElement
    // to access the shadow DOM.
    this.canvasRef = this.renderRoot.querySelector(
      'canvas',
    ) as HTMLCanvasElement;
    if (this.canvasRef) {
      this.canvasCtx = this.canvasRef.getContext('2d')!;
    }
  }

  updated(changedProperties: Map<string, unknown>) {
    if (this.videoElement) {
      // If videoElement is present, always prioritize it.
      if (changedProperties.has('videoElement')) {
        this.setupVideoVisualizer(this.videoElement);
      }
    } else if (this.inputNode) {
      // If no videoElement, but inputNode is present, use mic.
      if (
        changedProperties.has('inputNode') ||
        (changedProperties.has('videoElement') && !this.videoElement)
      ) {
        this.setupMicVisualizer(this.inputNode);
      }
    } else {
      // Neither is present, cleanup.
      this.sourceCleanup?.();
      this.sourceCleanup = null;
      this.analyser = undefined;
    }
  }

  private setupVideoVisualizer(videoEl: HTMLVideoElement) {
    this.sourceCleanup?.(); // Clean up previous source.
    try {
      const audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();

      // Resume context on play, as it may start in a suspended state.
      const resumeContext = () => {
        if (audioContext.state === 'suspended') {
          audioContext.resume();
        }
        // This listener is self-removing, but also removed in cleanup for safety.
        videoEl.removeEventListener('play', resumeContext);
      };
      videoEl.addEventListener('play', resumeContext);

      const source = audioContext.createMediaElementSource(videoEl);
      this.analyser = audioContext.createAnalyser();
      this.analyser.fftSize = 256;

      // Connect source to analyser, and analyser to destination so we can hear audio.
      source.connect(this.analyser);
      this.analyser.connect(audioContext.destination);

      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);

      this.sourceCleanup = () => {
        videoEl.removeEventListener('play', resumeContext);
        source.disconnect();
        this.analyser?.disconnect();
        audioContext.close();
      };

      if (!this.animationFrameId) {
        this.draw();
      }
    } catch (e) {
      console.error('Error setting up video audio visualizer:', e);
    }
  }

  private setupMicVisualizer(micInputNode: GainNode) {
    this.sourceCleanup?.(); // Clean up previous source.

    const audioContext = micInputNode.context as AudioContext;
    this.analyser = audioContext.createAnalyser();
    this.analyser.fftSize = 256;
    micInputNode.connect(this.analyser);
    this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);

    this.sourceCleanup = () => {
      // The micInputNode is managed by LiveChat, we should only disconnect our analyser from it.
      if (this.analyser) {
        try {
          micInputNode.disconnect(this.analyser);
        } catch (e) {
          // Ignore errors if already disconnected
        }
      }
    };

    if (!this.animationFrameId) {
      this.draw();
    }
  }

  draw() {
    this.animationFrameId = requestAnimationFrame(() => this.draw());
    if (
      !this.analyser ||
      !this.dataArray ||
      !this.canvasCtx ||
      !this.canvasRef
    ) {
      if (this.canvasCtx && this.canvasRef) {
        this.canvasCtx.fillStyle = '#111';
        this.canvasCtx.fillRect(
          0,
          0,
          this.canvasRef.width,
          this.canvasRef.height,
        );
      }
      return;
    }

    this.analyser.getByteFrequencyData(this.dataArray);

    this.canvasCtx.fillStyle = '#111';
    this.canvasCtx.fillRect(
      0,
      0,
      this.canvasRef.width,
      this.canvasRef.height,
    );

    const barWidth =
      (this.canvasRef.width / this.analyser.frequencyBinCount) * 2.5;
    let x = 0;

    for (let i = 0; i < this.analyser.frequencyBinCount; i++) {
      const barHeight = this.dataArray[i] / 2;
      this.canvasCtx.fillStyle = `rgb(${barHeight + 100}, 150, 250)`;
      this.canvasCtx.fillRect(
        x,
        this.canvasRef.height - barHeight,
        barWidth,
        barHeight,
      );
      x += barWidth + 1;
    }
  }

  render() {
    return html`<canvas></canvas>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'live-chat-visuals-3d': Visual3D;
  }
}
