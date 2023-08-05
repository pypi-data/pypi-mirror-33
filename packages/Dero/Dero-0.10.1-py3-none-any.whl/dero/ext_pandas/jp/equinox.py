"""
Equinox Day is a public holiday in Japan that usually occurs:
    (in the Spring) on March 20 or 21,
    (in the Autumn) on September 22 or 23,
the date of the equinox in Japan Standard Time.
Due to the necessity of recent astronomical measurements,
the date of the holiday is not officially declared until February of the previous year
We can't easily compute the equinox for a given year, so we pre-compute a list of those
from the Tokyo exchange inauguration to 2030 - the upper bound of pandas market calendars,
using pyephem (http://rhodesmill.org/pyephem/quick.html#equinoxes-solstices)
"""
import pandas as pd
from pandas.tseries.holiday import sunday_to_monday

vernal_mapping = {
    1878: pd.Timestamp('1878-03-21'),
    1879: pd.Timestamp('1879-03-21'),
    1880: pd.Timestamp('1880-03-20'),
    1881: pd.Timestamp('1881-03-20'),
    1882: pd.Timestamp('1882-03-21'),
    1883: pd.Timestamp('1883-03-21'),
    1884: pd.Timestamp('1884-03-20'),
    1885: pd.Timestamp('1885-03-20'),
    1886: pd.Timestamp('1886-03-21'),
    1887: pd.Timestamp('1887-03-21'),
    1888: pd.Timestamp('1888-03-20'),
    1889: pd.Timestamp('1889-03-20'),
    1890: pd.Timestamp('1890-03-21'),
    1891: pd.Timestamp('1891-03-21'),
    1892: pd.Timestamp('1892-03-20'),
    1893: pd.Timestamp('1893-03-20'),
    1894: pd.Timestamp('1894-03-20'),
    1895: pd.Timestamp('1895-03-21'),
    1896: pd.Timestamp('1896-03-20'),
    1897: pd.Timestamp('1897-03-20'),
    1898: pd.Timestamp('1898-03-20'),
    1899: pd.Timestamp('1899-03-21'),
    1900: pd.Timestamp('1900-03-21'),
    1901: pd.Timestamp('1901-03-21'),
    1902: pd.Timestamp('1902-03-21'),
    1903: pd.Timestamp('1903-03-22'),
    1904: pd.Timestamp('1904-03-21'),
    1905: pd.Timestamp('1905-03-21'),
    1906: pd.Timestamp('1906-03-21'),
    1907: pd.Timestamp('1907-03-22'),
    1908: pd.Timestamp('1908-03-21'),
    1909: pd.Timestamp('1909-03-21'),
    1910: pd.Timestamp('1910-03-21'),
    1911: pd.Timestamp('1911-03-22'),
    1912: pd.Timestamp('1912-03-21'),
    1913: pd.Timestamp('1913-03-21'),
    1914: pd.Timestamp('1914-03-21'),
    1915: pd.Timestamp('1915-03-22'),
    1916: pd.Timestamp('1916-03-21'),
    1917: pd.Timestamp('1917-03-21'),
    1918: pd.Timestamp('1918-03-21'),
    1919: pd.Timestamp('1919-03-22'),
    1920: pd.Timestamp('1920-03-21'),
    1921: pd.Timestamp('1921-03-21'),
    1922: pd.Timestamp('1922-03-21'),
    1923: pd.Timestamp('1923-03-22'),
    1924: pd.Timestamp('1924-03-21'),
    1925: pd.Timestamp('1925-03-21'),
    1926: pd.Timestamp('1926-03-21'),
    1927: pd.Timestamp('1927-03-21'),
    1928: pd.Timestamp('1928-03-21'),
    1929: pd.Timestamp('1929-03-21'),
    1930: pd.Timestamp('1930-03-21'),
    1931: pd.Timestamp('1931-03-21'),
    1932: pd.Timestamp('1932-03-21'),
    1933: pd.Timestamp('1933-03-21'),
    1934: pd.Timestamp('1934-03-21'),
    1935: pd.Timestamp('1935-03-21'),
    1936: pd.Timestamp('1936-03-21'),
    1937: pd.Timestamp('1937-03-21'),
    1938: pd.Timestamp('1938-03-21'),
    1939: pd.Timestamp('1939-03-21'),
    1940: pd.Timestamp('1940-03-21'),
    1941: pd.Timestamp('1941-03-21'),
    1942: pd.Timestamp('1942-03-21'),
    1943: pd.Timestamp('1943-03-21'),
    1944: pd.Timestamp('1944-03-21'),
    1945: pd.Timestamp('1945-03-21'),
    1946: pd.Timestamp('1946-03-21'),
    1947: pd.Timestamp('1947-03-21'),
    1948: pd.Timestamp('1948-03-21'),
    1949: pd.Timestamp('1949-03-21'),
    1950: pd.Timestamp('1950-03-21'),
    1951: pd.Timestamp('1951-03-21'),
    1952: pd.Timestamp('1952-03-21'),
    1953: pd.Timestamp('1953-03-21'),
    1954: pd.Timestamp('1954-03-21'),
    1955: pd.Timestamp('1955-03-21'),
    1956: pd.Timestamp('1956-03-21'),
    1957: pd.Timestamp('1957-03-21'),
    1958: pd.Timestamp('1958-03-21'),
    1959: pd.Timestamp('1959-03-21'),
    1960: pd.Timestamp('1960-03-20'),
    1961: pd.Timestamp('1961-03-21'),
    1962: pd.Timestamp('1962-03-21'),
    1963: pd.Timestamp('1963-03-21'),
    1964: pd.Timestamp('1964-03-20'),
    1965: pd.Timestamp('1965-03-21'),
    1966: pd.Timestamp('1966-03-21'),
    1967: pd.Timestamp('1967-03-21'),
    1968: pd.Timestamp('1968-03-20'),
    1969: pd.Timestamp('1969-03-21'),
    1970: pd.Timestamp('1970-03-21'),
    1971: pd.Timestamp('1971-03-21'),
    1972: pd.Timestamp('1972-03-20'),
    1973: pd.Timestamp('1973-03-21'),
    1974: pd.Timestamp('1974-03-21'),
    1975: pd.Timestamp('1975-03-21'),
    1976: pd.Timestamp('1976-03-20'),
    1977: pd.Timestamp('1977-03-21'),
    1978: pd.Timestamp('1978-03-21'),
    1979: pd.Timestamp('1979-03-21'),
    1980: pd.Timestamp('1980-03-20'),
    1981: pd.Timestamp('1981-03-21'),
    1982: pd.Timestamp('1982-03-21'),
    1983: pd.Timestamp('1983-03-21'),
    1984: pd.Timestamp('1984-03-20'),
    1985: pd.Timestamp('1985-03-21'),
    1986: pd.Timestamp('1986-03-21'),
    1987: pd.Timestamp('1987-03-21'),
    1988: pd.Timestamp('1988-03-20'),
    1989: pd.Timestamp('1989-03-21'),
    1990: pd.Timestamp('1990-03-21'),
    1991: pd.Timestamp('1991-03-21'),
    1992: pd.Timestamp('1992-03-20'),
    1993: pd.Timestamp('1993-03-20'),
    1994: pd.Timestamp('1994-03-21'),
    1995: pd.Timestamp('1995-03-21'),
    1996: pd.Timestamp('1996-03-20'),
    1997: pd.Timestamp('1997-03-20'),
    1998: pd.Timestamp('1998-03-21'),
    1999: pd.Timestamp('1999-03-21'),
    2000: pd.Timestamp('2000-03-20'),
    2001: pd.Timestamp('2001-03-20'),
    2002: pd.Timestamp('2002-03-21'),
    2003: pd.Timestamp('2003-03-21'),
    2004: pd.Timestamp('2004-03-20'),
    2005: pd.Timestamp('2005-03-20'),
    2006: pd.Timestamp('2006-03-21'),
    2007: pd.Timestamp('2007-03-21'),
    2008: pd.Timestamp('2008-03-20'),
    2009: pd.Timestamp('2009-03-20'),
    2010: pd.Timestamp('2010-03-21'),
    2011: pd.Timestamp('2011-03-21'),
    2012: pd.Timestamp('2012-03-20'),
    2013: pd.Timestamp('2013-03-20'),
    2014: pd.Timestamp('2014-03-21'),
    2015: pd.Timestamp('2015-03-21'),
    2016: pd.Timestamp('2016-03-20'),
    2017: pd.Timestamp('2017-03-20'),
    2018: pd.Timestamp('2018-03-21'),
    2019: pd.Timestamp('2019-03-21'),
    2020: pd.Timestamp('2020-03-20'),
    2021: pd.Timestamp('2021-03-20'),
    2022: pd.Timestamp('2022-03-21'),
    2023: pd.Timestamp('2023-03-21'),
    2024: pd.Timestamp('2024-03-20'),
    2025: pd.Timestamp('2025-03-20'),
    2026: pd.Timestamp('2026-03-20'),
    2027: pd.Timestamp('2027-03-21'),
    2028: pd.Timestamp('2028-03-20'),
    2029: pd.Timestamp('2029-03-20'),
    2030: pd.Timestamp('2030-03-20'),
    2031: pd.Timestamp('2031-03-21')
}

autumnal_mapping = {
    1878: pd.Timestamp('1878-09-23'),
    1879: pd.Timestamp('1879-09-23'),
    1880: pd.Timestamp('1880-09-23'),
    1881: pd.Timestamp('1881-09-23'),
    1882: pd.Timestamp('1882-09-23'),
    1883: pd.Timestamp('1883-09-23'),
    1884: pd.Timestamp('1884-09-23'),
    1885: pd.Timestamp('1885-09-23'),
    1886: pd.Timestamp('1886-09-23'),
    1887: pd.Timestamp('1887-09-23'),
    1888: pd.Timestamp('1888-09-22'),
    1889: pd.Timestamp('1889-09-23'),
    1890: pd.Timestamp('1890-09-23'),
    1891: pd.Timestamp('1891-09-23'),
    1892: pd.Timestamp('1892-09-22'),
    1893: pd.Timestamp('1893-09-23'),
    1894: pd.Timestamp('1894-09-23'),
    1895: pd.Timestamp('1895-09-23'),
    1896: pd.Timestamp('1896-09-22'),
    1897: pd.Timestamp('1897-09-23'),
    1898: pd.Timestamp('1898-09-23'),
    1899: pd.Timestamp('1899-09-23'),
    1900: pd.Timestamp('1900-09-23'),
    1901: pd.Timestamp('1901-09-24'),
    1902: pd.Timestamp('1902-09-24'),
    1903: pd.Timestamp('1903-09-24'),
    1904: pd.Timestamp('1904-09-23'),
    1905: pd.Timestamp('1905-09-24'),
    1906: pd.Timestamp('1906-09-24'),
    1907: pd.Timestamp('1907-09-24'),
    1908: pd.Timestamp('1908-09-23'),
    1909: pd.Timestamp('1909-09-24'),
    1910: pd.Timestamp('1910-09-24'),
    1911: pd.Timestamp('1911-09-24'),
    1912: pd.Timestamp('1912-09-23'),
    1913: pd.Timestamp('1913-09-24'),
    1914: pd.Timestamp('1914-09-24'),
    1915: pd.Timestamp('1915-09-24'),
    1916: pd.Timestamp('1916-09-23'),
    1917: pd.Timestamp('1917-09-24'),
    1918: pd.Timestamp('1918-09-24'),
    1919: pd.Timestamp('1919-09-24'),
    1920: pd.Timestamp('1920-09-23'),
    1921: pd.Timestamp('1921-09-23'),
    1922: pd.Timestamp('1922-09-24'),
    1923: pd.Timestamp('1923-09-24'),
    1924: pd.Timestamp('1924-09-23'),
    1925: pd.Timestamp('1925-09-23'),
    1926: pd.Timestamp('1926-09-24'),
    1927: pd.Timestamp('1927-09-24'),
    1928: pd.Timestamp('1928-09-23'),
    1929: pd.Timestamp('1929-09-23'),
    1930: pd.Timestamp('1930-09-24'),
    1931: pd.Timestamp('1931-09-24'),
    1932: pd.Timestamp('1932-09-23'),
    1933: pd.Timestamp('1933-09-23'),
    1934: pd.Timestamp('1934-09-24'),
    1935: pd.Timestamp('1935-09-24'),
    1936: pd.Timestamp('1936-09-23'),
    1937: pd.Timestamp('1937-09-23'),
    1938: pd.Timestamp('1938-09-24'),
    1939: pd.Timestamp('1939-09-24'),
    1940: pd.Timestamp('1940-09-23'),
    1941: pd.Timestamp('1941-09-23'),
    1942: pd.Timestamp('1942-09-24'),
    1943: pd.Timestamp('1943-09-24'),
    1944: pd.Timestamp('1944-09-23'),
    1945: pd.Timestamp('1945-09-23'),
    1946: pd.Timestamp('1946-09-24'),
    1947: pd.Timestamp('1947-09-24'),
    1948: pd.Timestamp('1948-09-23'),
    1949: pd.Timestamp('1949-09-23'),
    1950: pd.Timestamp('1950-09-23'),
    1951: pd.Timestamp('1951-09-24'),
    1952: pd.Timestamp('1952-09-23'),
    1953: pd.Timestamp('1953-09-23'),
    1954: pd.Timestamp('1954-09-23'),
    1955: pd.Timestamp('1955-09-24'),
    1956: pd.Timestamp('1956-09-23'),
    1957: pd.Timestamp('1957-09-23'),
    1958: pd.Timestamp('1958-09-23'),
    1959: pd.Timestamp('1959-09-24'),
    1960: pd.Timestamp('1960-09-23'),
    1961: pd.Timestamp('1961-09-23'),
    1962: pd.Timestamp('1962-09-23'),
    1963: pd.Timestamp('1963-09-24'),
    1964: pd.Timestamp('1964-09-23'),
    1965: pd.Timestamp('1965-09-23'),
    1966: pd.Timestamp('1966-09-23'),
    1967: pd.Timestamp('1967-09-24'),
    1968: pd.Timestamp('1968-09-23'),
    1969: pd.Timestamp('1969-09-23'),
    1970: pd.Timestamp('1970-09-23'),
    1971: pd.Timestamp('1971-09-24'),
    1972: pd.Timestamp('1972-09-23'),
    1973: pd.Timestamp('1973-09-23'),
    1974: pd.Timestamp('1974-09-23'),
    1975: pd.Timestamp('1975-09-24'),
    1976: pd.Timestamp('1976-09-23'),
    1977: pd.Timestamp('1977-09-23'),
    1978: pd.Timestamp('1978-09-23'),
    1979: pd.Timestamp('1979-09-24'),
    1980: pd.Timestamp('1980-09-23'),
    1981: pd.Timestamp('1981-09-23'),
    1982: pd.Timestamp('1982-09-23'),
    1983: pd.Timestamp('1983-09-23'),
    1984: pd.Timestamp('1984-09-23'),
    1985: pd.Timestamp('1985-09-23'),
    1986: pd.Timestamp('1986-09-23'),
    1987: pd.Timestamp('1987-09-23'),
    1988: pd.Timestamp('1988-09-23'),
    1989: pd.Timestamp('1989-09-23'),
    1990: pd.Timestamp('1990-09-23'),
    1991: pd.Timestamp('1991-09-23'),
    1992: pd.Timestamp('1992-09-23'),
    1993: pd.Timestamp('1993-09-23'),
    1994: pd.Timestamp('1994-09-23'),
    1995: pd.Timestamp('1995-09-23'),
    1996: pd.Timestamp('1996-09-23'),
    1997: pd.Timestamp('1997-09-23'),
    1998: pd.Timestamp('1998-09-23'),
    1999: pd.Timestamp('1999-09-23'),
    2000: pd.Timestamp('2000-09-23'),
    2001: pd.Timestamp('2001-09-23'),
    2002: pd.Timestamp('2002-09-23'),
    2003: pd.Timestamp('2003-09-23'),
    2004: pd.Timestamp('2004-09-23'),
    2005: pd.Timestamp('2005-09-23'),
    2006: pd.Timestamp('2006-09-23'),
    2007: pd.Timestamp('2007-09-23'),
    2008: pd.Timestamp('2008-09-23'),
    2009: pd.Timestamp('2009-09-23'),
    2010: pd.Timestamp('2010-09-23'),
    2011: pd.Timestamp('2011-09-23'),
    2012: pd.Timestamp('2012-09-22'),
    2013: pd.Timestamp('2013-09-23'),
    2014: pd.Timestamp('2014-09-23'),
    2015: pd.Timestamp('2015-09-23'),
    2016: pd.Timestamp('2016-09-22'),
    2017: pd.Timestamp('2017-09-23'),
    2018: pd.Timestamp('2018-09-23'),
    2019: pd.Timestamp('2019-09-23'),
    2020: pd.Timestamp('2020-09-22'),
    2021: pd.Timestamp('2021-09-23'),
    2022: pd.Timestamp('2022-09-23'),
    2023: pd.Timestamp('2023-09-23'),
    2024: pd.Timestamp('2024-09-22'),
    2025: pd.Timestamp('2025-09-23'),
    2026: pd.Timestamp('2026-09-23'),
    2027: pd.Timestamp('2027-09-23'),
    2028: pd.Timestamp('2028-09-22'),
    2029: pd.Timestamp('2029-09-23'),
    2030: pd.Timestamp('2030-09-23'),
    2031: pd.Timestamp('2030-09-23'),
}

def vernal_equinox(dt):
    year = dt.year
    equinox = vernal_mapping[year]
    return sunday_to_monday(equinox)

def autumnal_equinox(dt):
    year = dt.year
    equinox = autumnal_mapping[year]
    return sunday_to_monday(equinox)