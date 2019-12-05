-- Number of orders by state
-- from both online (shipping state) and in-store (store-state)
SELECT State, Count(*)
FROM 
(
    SELECT State
    FROM CusOrder
    INNER JOIN Address USING (AddressID)
    UNION ALL
    SELECT State
    FROM CusOrder
    INNER JOIN Stock USING (SiteID)
    INNER JOIN Address ON Stock.AddressID = Address.AddressID
    WHERE Stock.StockType = 'store'
) tmpt
GROUP BY State;

-- Average order sale by state
SELECT State, AVG(OrderPrice)
FROM 
(
    SELECT State, OrderPrice
    FROM CusOrder
    INNER JOIN Address USING (AddressID)
    UNION ALL
    SELECT State, OrderPrice
    FROM CusOrder
    INNER JOIN Stock USING (SiteID)
    INNER JOIN Address ON Stock.AddressID = Address.AddressID
    WHERE Stock.StockType = 'store'
) tmpt
GROUP BY State;

-- Daily order sale
SELECT DATE(OrderTime) as OrderDate, SUM(OrderPrice)
FROM CusOrder
GROUP BY OrderDate 
ORDER BY OrderDate ASC;

-- Monthly sale changes in percentage
with OrderPriceLast(OrderTime, LastPrice) AS 
    (
        SELECT DATE_ADD(OrderTime, INTERVAL 1 MONTH), 
            OrderPrice 
        From CusOrder
    ),
    OrderPriceThis(OrderTIme, ThisPrice) AS
    (
        SELECT OrderTime, OrderPrice
        From CusOrder
    )
SELECT ThisPrices.OrderYear, ThisPrices.OrderMonth, (ThisSales - LastSales)/LastSales*100
FROM
(
    SELECT YEAR(OrderTime) AS OrderYear, MONTH(OrderTime) as OrderMonth, SUM(ThisPrice) as ThisSales
    FROM OrderPriceThis
    GROUP BY OrderYear, OrderMonth
) ThisPrices
INNER JOIN
(
    SELECT YEAR(OrderTime) AS OrderYear, MONTH(OrderTime) as OrderMonth, SUM(LastPrice) as LastSales
    FROM OrderPriceLast
    GROUP BY OrderYear, OrderMonth
) LastPrices
ON ThisPrices.OrderYear = LastPrices.OrderYear AND ThisPrices.OrderMonth = LastPrices.OrderMonth