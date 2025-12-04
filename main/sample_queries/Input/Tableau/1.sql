-- Customer analytics extract for Tableau → Fabric conversion test
SELECT
    [CustomerID],
    [CustomerName],
    [Region],
    [Segment],

    -- String functions
    SUBSTR([CustomerName], 1, 5) AS NameStart,
    SPLIT([Email], '@', 1) AS EmailUser,
    LENGTH([CustomerName]) AS NameLength,
    FIND([CustomerName], ' ') AS SpacePos,

    -- Boolean logic
    IF([Region] = 'West' THEN TRUE ELSE FALSE END) AS IsWest,

    -- Contains / startswith / endswith
    CONTAINS([CustomerName], 'Inc') AS HasInc,
    STARTSWITH([CustomerName], 'A') AS StartsWithA,
    ENDSWITH([CustomerName], 'LLC') AS EndsWithLLC,

    -- Date functions
    NOW() AS CurrentTS,
    TODAY() AS CurrentDate,
    DATEADD('day', -30, NOW()) AS Last30Days,
    MAKEDATE(2024, 1, 15) AS BuiltDate,
    MAKEDATETIME(2023, 12, 25, 10, 30, 00) AS BuiltDatetime,

    -- Numeric conversion
    INT([Age]) AS AgeInt,
    FLOAT([Revenue]) AS RevFloat,
    STR([Revenue]) AS RevString,
    DATE([SignupDate]) AS SignupDateCast,

    -- Math
    LN([Revenue]) AS LogRev,
    LOG([Revenue]) AS Log10Rev,

    -- Null handling
    IFNULL([Profit], 0) AS ProfitNZ,

    -- Median test (your parser should flag this)
    MEDIAN([Revenue]) AS MedianRevenue,

    -- LOD test (your parser must flag this)
    { FIXED [Region] : SUM([Revenue]) } AS RegionalRevenueLOD
FROM CustomerTable
WHERE CONTAINS([Email], 'gmail')
