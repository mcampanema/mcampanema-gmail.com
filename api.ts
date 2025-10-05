/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
/* tslint:disable */

import {
  FunctionDeclaration,
  GoogleGenAI,
  Part,
  File as GenAIFile,
  Type,
} from '@google/genai';

const systemInstruction = `When given a video and a query, call the relevant \
function only once with the appropriate timecodes and text for the video`;

const client = new GoogleGenAI({apiKey: process.env.API_KEY});

async function generateContent(
  text: string,
  functionDeclarations: FunctionDeclaration[],
  file: GenAIFile | null,
  youtubeUrl?: string,
) {
  const userParts: Part[] = [];
  let promptText = text;

  if (youtubeUrl) {
    promptText = `${text}\n\nAnalyze the following YouTube video, providing timecodes relative to the video's timeline: ${youtubeUrl}`;
  }
  userParts.push({text: promptText});

  if (file) {
    userParts.push({
      fileData: {
        mimeType: file.mimeType,
        fileUri: file.uri,
      },
    });
  }

  const response = await client.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: [
      {
        role: 'user',
        parts: userParts,
      },
    ],
    config: {
      systemInstruction,
      temperature: 0.5,
      tools: [{functionDeclarations}],
    },
  });

  return response;
}

async function uploadFile(file: File): Promise<GenAIFile> {
  const blob = new Blob([file], {type: file.type});

  console.log('Uploading...');
  const uploadedFile = await client.files.upload({
    file: blob,
    config: {
      displayName: file.name,
    },
  });
  console.log('Uploaded.');
  console.log('Getting...');
  let getFile = await client.files.get({
    name: uploadedFile.name,
  });
  while (getFile.state === 'PROCESSING') {
    getFile = await client.files.get({
      name: uploadedFile.name,
    });
    console.log(`current file status: ${getFile.state}`);
    console.log('File is still processing, retrying in 5 seconds');

    await new Promise((resolve) => {
      setTimeout(resolve, 5000);
    });
  }
  console.log(getFile.state);
  if (getFile.state === 'FAILED') {
    throw new Error('File processing failed.');
  }
  console.log('Done');
  return getFile;
}

interface YouTubeSearchResult {
  videoId: string;
  title: string;
  thumbnailUrl: string;
}

async function searchYoutubeVideos(
  query: string,
): Promise<YouTubeSearchResult[]> {
  try {
    const response = await client.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: `Find 5 relevant YouTube videos about "${query}". Provide the video ID, title, and thumbnail URL for each.`,
      config: {
        responseMimeType: 'application/json',
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              videoId: {
                type: Type.STRING,
                description: 'The 11-character YouTube video ID.',
              },
              title: {
                type: Type.STRING,
                description: 'The title of the YouTube video.',
              },
              thumbnailUrl: {
                type: Type.STRING,
                description:
                  'The URL for the video thumbnail image, typically from i.ytimg.com.',
              },
            },
            required: ['videoId', 'title', 'thumbnailUrl'],
          },
        },
      },
    });

    const jsonString = response.text.trim();
    const result = JSON.parse(jsonString);

    if (!Array.isArray(result)) {
      throw new Error('API did not return a valid array of search results.');
    }

    // Basic validation of the returned structure
    return result.filter(
      (item) =>
        item &&
        typeof item.videoId === 'string' &&
        typeof item.title === 'string' &&
        typeof item.thumbnailUrl === 'string',
    );
  } catch (error) {
    console.error('Error searching YouTube videos:', error);
    throw new Error(
      `Failed to search YouTube. The model may be unable to find results for your query. Original error: ${
        (error as Error).message
      }`,
    );
  }
}

export {generateContent, uploadFile, searchYoutubeVideos};