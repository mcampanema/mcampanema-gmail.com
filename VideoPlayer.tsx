/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
/* tslint:disable */
// Copyright 2024 Google LLC

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     https://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, {useCallback, useEffect, useMemo, useState} from 'react';

const formatTime = (t: number) =>
  `${Math.floor(t / 60)}:${Math.floor(t % 60)
    .toString()
    .padStart(2, '0')}`;

interface YouTubeSearchResult {
  videoId: string;
  title: string;
  thumbnailUrl: string;
}

export default function VideoPlayer({
  url,
  video,
  setVideo,
  youtubeVideoId,
  youtubeUrlInput,
  onYoutubeUrlChange,
  onYoutubeUrlSubmit,
  isLoadingVideo,
  videoError,
  videoMimeType,
  youtubeSearchQuery,
  onYoutubeSearchQueryChange,
  onYoutubeSearchSubmit,
  isSearchingYoutube,
  youtubeSearchResults,
  youtubeSearchError,
  onSelectSearchResult,
}: {
  url: string | null;
  video: HTMLVideoElement | null;
  setVideo: (video: HTMLVideoElement | null) => void;
  youtubeVideoId: string | null;
  youtubeUrlInput: string;
  onYoutubeUrlChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onYoutubeUrlSubmit: () => void;
  isLoadingVideo: boolean;
  videoError: string | null;
  videoMimeType: string | null;
  youtubeSearchQuery: string;
  onYoutubeSearchQueryChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onYoutubeSearchSubmit: () => void;
  isSearchingYoutube: boolean;
  youtubeSearchResults: YouTubeSearchResult[];
  youtubeSearchError: string | null;
  onSelectSearchResult: (videoId: string) => void;
}) {
  const [duration, setDuration] = useState(0);
  const [scrubberTime, setScrubberTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isScrubbing, setIsScrubbing] = useState(false);
  const [activeTab, setActiveTab] = useState<'url' | 'search'>('url');
  const currentSecs = duration * scrubberTime || 0;
  const currentPercent = scrubberTime * 100;

  const youtubeSrc = useMemo(() => {
    if (!youtubeVideoId) return '';
    return `https://www.youtube.com/embed/${youtubeVideoId}?enablejsapi=1`;
  }, [youtubeVideoId]);

  const togglePlay = useCallback(() => {
    if (!video) return;
    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
  }, [isPlaying, video]);

  const updateDuration = () => setDuration(video!.duration);

  const updateTime = () => {
    if (!video) return;
    if (!isScrubbing) {
      setScrubberTime(video.currentTime / video.duration);
    }
  };

  const onPlay = () => setIsPlaying(true);
  const onPause = () => setIsPlaying(false);

  useEffect(() => {
    setScrubberTime(0);
    setIsPlaying(false);
  }, [url, youtubeVideoId]);

  useEffect(() => {
    const onKeyPress = (e: KeyboardEvent) => {
      if (
        e.target instanceof HTMLElement &&
        e.target.tagName !== 'INPUT' &&
        e.target.tagName !== 'TEXTAREA' &&
        e.key === ' '
      ) {
        togglePlay();
      }
    };

    window.addEventListener('keypress', onKeyPress);

    return () => {
      window.removeEventListener('keypress', onKeyPress);
    };
  }, [togglePlay]);

  const renderEmptyState = () => (
    <div className="emptyVideo">
      {isLoadingVideo ? (
        <p>Processing...</p>
      ) : (
        <div className="emptyVideoContent">
          <p>Drag and drop a video file here</p>
          <span className="or-divider">or</span>

          <div className="video-input-container">
            <div className="video-input-tabs">
              <button
                className={activeTab === 'url' ? 'active' : ''}
                onClick={() => setActiveTab('url')}>
                Paste URL
              </button>
              <button
                className={activeTab === 'search' ? 'active' : ''}
                onClick={() => setActiveTab('search')}>
                Search YouTube
              </button>
            </div>

            {activeTab === 'url' ? (
              <div className="youtube-input-container">
                <input
                  type="text"
                  placeholder="Paste a YouTube URL"
                  value={youtubeUrlInput}
                  onChange={onYoutubeUrlChange}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') onYoutubeUrlSubmit();
                  }}
                />
                <button onClick={onYoutubeUrlSubmit}>Analyze</button>
              </div>
            ) : (
              <div className="youtube-input-container">
                <input
                  type="text"
                  placeholder="Search for a YouTube video"
                  value={youtubeSearchQuery}
                  onChange={onYoutubeSearchQueryChange}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') onYoutubeSearchSubmit();
                  }}
                />
                <button onClick={onYoutubeSearchSubmit}>Search</button>
              </div>
            )}
          </div>

          {videoError && <p className="error-message">{videoError}</p>}

          {isSearchingYoutube && <p>Searching...</p>}
          {youtubeSearchError && (
            <p className="error-message">{youtubeSearchError}</p>
          )}

          {youtubeSearchResults.length > 0 && (
            <div className="youtube-search-results">
              {youtubeSearchResults.map((result) => (
                <div
                  key={result.videoId}
                  className="search-result-item"
                  onClick={() => onSelectSearchResult(result.videoId)}
                  role="button"
                  tabIndex={0}>
                  <img src={result.thumbnailUrl} alt={result.title} />
                  <p>{result.title}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );

  return (
    <div className="videoPlayer">
      {youtubeVideoId ? (
        <iframe
          key={youtubeSrc} // Re-renders iframe when src changes
          src={youtubeSrc}
          title="YouTube video player"
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowFullScreen
          style={{width: '100%', height: '100%'}}></iframe>
      ) : url && !isLoadingVideo ? (
        <>
          <div>
            <video
              key={url}
              ref={setVideo}
              onClick={togglePlay}
              preload="auto"
              crossOrigin="anonymous"
              onDurationChange={updateDuration}
              onTimeUpdate={updateTime}
              onPlay={onPlay}
              onPause={onPause}>
              {videoMimeType && <source src={url} type={videoMimeType} />}
            </video>
          </div>

          <div className="videoControls">
            <div className="videoScrubber">
              <input
                style={{'--pct': `${currentPercent}%`} as React.CSSProperties}
                type="range"
                min="0"
                max="1"
                value={scrubberTime || 0}
                step="0.000001"
                onChange={(e) => {
                  if (!video) return;
                  const value = (e.target as HTMLInputElement).valueAsNumber;
                  setScrubberTime(value);
                  video.currentTime = value * duration;
                }}
                onPointerDown={() => setIsScrubbing(true)}
                onPointerUp={() => setIsScrubbing(false)}
              />
            </div>

            <div className="videoTime">
              <button onClick={togglePlay}>
                <span className="icon">
                  {isPlaying ? 'pause' : 'play_arrow'}
                </span>
              </button>
              {formatTime(currentSecs)} / {formatTime(duration)}
            </div>
          </div>
        </>
      ) : (
        renderEmptyState()
      )}
    </div>
  );
}