## Questions
What is this API being used for?
- Do we care about insertion performance?
  - As in, are we inserting to this dataset often?
- Do we care about query performance?
  - As in, are we querying it often?
- Which one do we want to prioritize?
  - I'm assuming that we want to prioritize both for now.

## Assumptions
- ID is unique
- numerical value is `int32`
- X must also be `int32`
- The data already exists in the server, so we don't need to worry about upload
- Data is not sorted by id nor value

## Initial Considerations
1. Performance
   1. This goes back to the question at the beginning, what do we want to optimize?
   2. Query
      1. With the assumption that the data is un-sorted
         1. We will have to go through every single data point to check
         2. `O(n)`
      2. If the data is sorted
         1. It takes a constant time, we can simply get the top X, as I'd have sorted the data by max numerical value
         2. `O(1)`
   3. Insertion
      1. If the data is unsorted
         1. We can just append to the end of the file
         2. `O(1)`
      2. If the data is sorted
         1. This can be optimized by using a binary search to find where we need to insert the new data, it'd be `O(log n)`
         2. But this depends on how we're storing the data
            1. If csv/some sort of file
               1. It'd be `O(n)` just to actually write the bytes to the file
            2. If it's an indexed database (index on the numerical value)
               1. `O(log n)`
2. Memory
   1. For practical purposes, I generated 10 million rows, but this needs to be scalable to an even larger dataset
   2. I will treat it as if it's a massive dataset (terabytes)
      1. So I will have to chunk it, and not load everything in memory

## Approaches:
1. Letting the data sit as is, no modifications.
   1. This is difficult to deal with. Since we'll need to parse the string `<numerical_id>_<numerical_value>` if we want to compare (get the max)
   2. Pros:
      1. Keeping the data as is
      2. Easy to insert new data, since we don't have to do any processing
   3. Cons:
      1. We need to parse the string to do comparisons
         1. This means if we query this more than once, we're essentially doing the work that we've already done all over again (parsing strings)
   4. That means, this approach should only be used IF:
      1. The data won't change
      2. We only need to query once
   5. We should not use this approach if:
      1. The data changes
      2. We're query-ing multiple times
      3. We care about the data updates, since it might affect our query
2. Sorting the data
   1. With pandas, we create a dataframe
      1. The library abstracts chunking of the data.
   2. Normalize it (split string by `_`) and create 2 separated columns of `numerical_id` and `numerical_value`
   3. Sort it `O(n log n)`
   4. Query-ing is `O(X)`
      1. Where `X` is the number of top values requested
   5. Pros:
      1. Very efficient query time
   6. Cons:
      1. Expensive to setup (need to sort)
      2. Insertion is expensive, as we need to ensure to insert into the right position.
         1. Searching where to insert can take `O(log n)`
         2. Insertion itself can take `O(n)`, as we'd need to shift everything down by 1.
      3. This needs to be in memory. In extremely large datasets, this is not feasible
   7. We should use this approach if:
      1. We are okay with expensive set up (initial sorting)
      2. We need good query performance
      3. We are okay with an in memory approach.
3. Not sorting the data
   1. Same as sorting the data steps 1 and 2
   2. query is `O(n)`
   3. Insertion is `O(1)`
   4. We should use this approach if:
      1. We don't query often at all, so we're okay with more expensive query.
      2. We care a lot about insertion performance
4. Indexed Database
   1. Create a descending index on the numerical_value
   2. Query is `O(log N)`
   3. Insertion is optimized to `O(log N)`
   4. Now this depends on the specific database implementation
      1. MongoDB uses a B Tree to implement indices
   5. Creating and indexing database for very large data can be very expensive.

## Actual performance
### In memory approach using pandas
`O(X)`
Query is less than a second on average.

This approach is faster when the dataset is smaller because there is no network overhead.

### Indexed database
1. It took 1973.5415353999706 seconds or about 32 minutes to insert all 10M rows of data
   1. This database tier allows for a maximum of 500 ops/sec
   2. MongoDB adds a unique id to every row and it indexes it. So this will add to the cost of this operation.
2. It took 102.33526829996845 seconds to create an index for `numerical_value`
3. `O(Log N)` on average
   1. This grows to `O(N)` when `X == N` as an edge case
4. This approach is more efficient and scalable when datasets become extremely large.

## Things I would add/investigate if I had more time
- Explore the usage of Data Lake instead of nosql
  - I've never used it before, but it seems like it's designed for large scale parallel processing.
  - This MIGHT be useful, as it can sort in parallel. But would have to investigate
- Multithreading in the in memory approach.
  - Sorting with multithreading is a difficult problem. But if used, it can optimize it
- For the API design itself
  - Use a singleton class that maintains a single pool of connection
  - Then I would use a getter function to get a connection, instead of re-establishing one each time the endpoint is called