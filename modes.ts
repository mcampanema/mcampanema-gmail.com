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

export default {
  'A/V captions': {
    emoji: '👀',
    prompt: `Generate captions for each scene in this video. Describe the visuals and include any spoken text in quotation marks. For each caption, provide the start time. Format the output as a list, like this:
[00:15] - A person walks into the room.
[00:22] - "Hello there!"`,
    isList: true,
  },

  Paragraph: {
    emoji: '📝',
    prompt: `Generate a paragraph that summarizes this video. Keep it to 3 to 5 sentences. At the end of each sentence, include the relevant timestamp from the video in brackets, like this: [00:45].`,
  },

  'Key moments': {
    emoji: '🔑',
    prompt: `Generate a bulleted list of key moments from the video. For each bullet point, include the relevant timestamp from the video. Format it like this:
- [01:10] The main character discovers the hidden treasure.`,
    isList: true,
  },

  Table: {
    emoji: '🤓',
    prompt: `Create a markdown table of 5 key shots from this video. The table should have three columns: "Timecode", "Description" (10 words or less), and "Objects" (a list of visible objects with emojis).`,
  },

  Haiku: {
    emoji: '🌸',
    prompt: `Generate a haiku about the video. After each line, provide the most relevant timestamp from the video in brackets, like this: [00:30]. Make sure to follow the 5-7-5 syllable rule.`,
  },

  Chart: {
    emoji: '📈',
    prompt: (input: string) =>
      `Generate chart data for this video based on the following instructions: ${input}. Call set_timecodes_with_numeric_values once with the list of data values and timecodes.`,
    subModes: {
      Excitement:
        'for each scene, estimate the level of excitement on a a scale of 1 to 10',
      Importance:
        'for each scene, estimate the level of overall importance to the video on a scale of 1 to 10',
      'Number of people': 'for each scene, count the number of people visible',
    },
  },

  Custom: {
    emoji: '🔧',
    prompt: (input: string) =>
      `Call set_timecodes once using the following instructions: ${input}`,
    isList: true,
  },
} as const;