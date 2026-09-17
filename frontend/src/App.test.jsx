import { describe, expect, it } from 'vitest';
import { sites } from './data';

describe('portfolio fixture', () => {
  it('contains sites with positive areas', () => {
    expect(sites).toHaveLength(4);
    expect(sites.every((site) => site.hectares > 0)).toBe(true);
  });
});
