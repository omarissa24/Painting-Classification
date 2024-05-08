# Optimized Exhibition Opening - Team 961s

## Project Overview
This project focuses on processing and categorizing paintings into landscape and portrait types, generating frameglasses based on painting tags, and merging portraits using a set of defined criteria to maximize local score. 

## Objectives
- **Parse files**: To parse files containing information about paintings.
- **Categorize paintings**: Categorize them into landscape and portrait types.
- **Generate frameglasses**: Generate frameglasses for each painting based on its tags.
- **Merge portraits**: Merge the portraits according to criteria that maximize the local score.

## Strategies
### Processing Paintings
- **Landscape Tags**: Dictionary storing sets of tags for landscape paintings.
- **Portrait Tags**: Dictionary storing sets of tags for portrait paintings.
- **Tag Frameglasses**: Dictionary storing frameglasses that contain a particular tag.
- **Frameglasses Array**: Array of frameglasses with their indexes and tags.
- **Merging Portraits**: Sort frameglasses by the number of tags in descending order and merge portraits based on the lowest common tags to maximize the score.

### Merging Portraits
- Implementing a greedy approach to find the best possible pairing.
- Sort portrait_tags by the length of their tag sets in descending order.
- Process in batches to avoid duplications and optimize pairing based on the lowest common tags.

### Maximizing Satisfaction
- Sort the array in descending order based on the number of tags.
- Use brute force to find the best match in smaller batches and combine them for higher order combinations.
- Adjust batch sizes to balance between runtime and score optimization.

### Binary Landscapes Approach
- Utilize a dictionary (`tag_frameglasses`) to match landscapes with common tags.
- Sort frameglasses by tag frequency and pair them to maximize local scoring.

## Results
- Achieved a consistent score of approximately 1,028,000 in under 28 minutes using a single-core process without parallel computing.

## Future Directions
- Explore genetic algorithms to optimize batch sizes further.
- Investigate alternative methods for combining portraits to improve scores.
