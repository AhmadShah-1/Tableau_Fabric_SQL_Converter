-- Customer analytics extract for Tableau -> Fabric conversion test
SELECT
    CustomerID,
    CustomerName,
    Region,
    Segment,

    -- String functions
    SUBSTRING(CustomerName, 1, 5) AS NameStart,
    SUBSTRING(Email, 1, CHARINDEX('@', Email) - 1) AS EmailUser,
    LEN(CustomerName) AS NameLength,
    CHARINDEX(' ', CustomerName) AS SpacePos,

    -- Boolean logic
    IIF(CustomerName = 'West' THEN 1 ELSE 0 END) AS IsWest,

    -- Contains / startswith / endswith
    CHARINDEX('Inc', CustomerName) > 0 AS HasInc,
    CHARINDEX('A', CustomerName) = 1 AS StartsWithA,
    RIGHT(CustomerName, LEN('LLC')) = 'LLC' AS EndsWithLLC,

    -- Date functions
    GETDATE() AS CurrentTS,
    CAST(GETDATE() AS DATE) AS CurrentDate,
    DATEADD('day', -30, GETDATE()) AS Last30Days,
    DATEFROMPARTS(2024, 1, 15) AS BuiltDate,
    DATETIMEFROMPARTS(2023, 12, 25, 10, 30, 00) AS BuiltDatetime,

    -- Numeric conversion
    CAST(Age AS INT) AS AgeInt,
    CAST(Revenue AS FLOAT) AS RevFloat,
    CAST(Revenue AS VARCHAR(20)) AS RevString,
    CAST(SignupDate AS DATE) AS SignupDateCast,

    -- Math
    LOG(Revenue) AS LogRev,        -- LN() → LOG()
    LOG10(Revenue) AS Log10Rev,    -- LOG() → LOG10()

    -- Null handling
    ISNULL(Profit, 0) AS ProfitNZ,

    -- Median (flagged)
    MEDIAN(Revenue) AS MedianRevenue,

    -- LOD (flagged)
    { FIXED Region : SUM(Revenue) } AS RegionalRevenueLOD

FROM CustomerTable
WHERE CHARINDEX('gmail', Email) > 0;
