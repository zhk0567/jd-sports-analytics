import type { StoryData } from "./types";

export async function loadStory(): Promise<StoryData> {
  const res = await fetch(`/data/story.json?t=${Date.now()}`);
  if (!res.ok) {
    throw new Error(`Failed to load story.json (${res.status})`);
  }
  return (await res.json()) as StoryData;
}
