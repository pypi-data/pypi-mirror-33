/*
  calendrical2.c (beta): Written by Tadayoshi Funaba 1997,1999-2002,2014

  This code is in the public domain, but any use of it
  should publically acknowledge its source.

  $Id: calendrical2.c,v 1.10 2014-04-27 09:42:02+09 tadf Exp $
*/

#define MODULE

#ifndef NULL
#define NULL 0
#endif

#include <stdlib.h>
#include <math.h>
#include "calendrical.h"
#include "calendrical2.h"

static div_t
divmod(int m, int n)
{
  div_t d;

  d = div(m, n);
  if ((m < 0) != (n < 0) && d.rem != 0) {
    d.quot -= 1;
    d.rem += n;
  }
  return d;
}

#undef quotient
#define quotient(m, n) i_quotient(m, n)
static int
i_quotient(int m, int n)
{
  return divmod(m, n).quot;
}
#undef mod
#define mod(m, n) i_mod(m, n)
static int
i_mod(int m, int n)
{
  return divmod(m, n).rem;
}
#undef oddp
#define oddp(n) ((n) % 2)

static int
approximate(int x, int y)
{
  return quotient(x, (x < 0) ? (y - 1) : y);
}

int
world_leap_year(int year)
{
  return
    mod(year, 4) == 0 &&
    !(mod(year, 400) == 100 ||
      mod(year, 400) == 200 ||
      mod(year, 400) == 300);
}

int
world_last_day_of_month(int year, int month)
{
  if (month == 6 && world_leap_year(year))
    return 31;
  switch (month) {
  case  1: return 31;
  case  2: return 30;
  case  3: return 30;
  case  4: return 31;
  case  5: return 30;
  case  6: return 30;
  case  7: return 31;
  case  8: return 30;
  case  9: return 30;
  case 10: return 31;
  case 11: return 30;
  case 12: return 31;
  default: return 0;
  }
}

int
world_to_rd(int year, int month, int day)
{
  int sumres;

  {
    int temp, m;
    for (temp = 0, m = 1;
	 (m < month);
	 temp = temp + world_last_day_of_month(year, m), m++)
      ;
    sumres = temp;
  }
  return day
    + sumres
    + (365 * (year - 1))
    + quotient(year - 1, 4)
    - quotient(year - 1, 100)
    + quotient(year - 1, 400);
}

void
rd_to_world(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, month, day, year;
  int sumres1, sumres2;

  approx = approximate(date, 366);
  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= world_to_rd(1 + y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > world_to_rd
	  (year, m, world_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date
    - (world_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
rd_to_world_day_of_week(int date)
{
  int month, day, year;

  rd_to_world(date, &year, &month, &day);
  if (month == 12 && day == 31)
    return 7;
  else if (month == 6 && day == 31)
    return 8;
  else
    switch ((month - 1) % 3) {
    case 0: return (day - 1) % 7;
    case 1: return (day + 2) % 7;
    case 2: return (day + 4) % 7;
    }
  /*NOTREACHED*/
  return -1;
}

int
coptic_leap_year(int year)
{
  return mod(year, 4) == 3;
}

int
coptic_last_day_of_month(int year, int month)
{
  if (month == 13 && coptic_leap_year(year))
    return 6;
  switch (month) {
  case  1: return 30;
  case  2: return 30;
  case  3: return 30;
  case  4: return 30;
  case  5: return 30;
  case  6: return 30;
  case  7: return 30;
  case  8: return 30;
  case  9: return 30;
  case 10: return 30;
  case 11: return 30;
  case 12: return 30;
  case 13: return 5;
  default: return 0;
  }
}

#define EPOCH_COPTIC 103605
#define BEFORE_COPTIC (103605 - 1)

int
coptic_to_rd(int year, int month, int day)
{
  int sumres;

  {
    int temp, m;
    for (temp = 0, m = 1;
	 (m < month);
	 temp = temp + coptic_last_day_of_month(year, m), m++)
      ;
    sumres = temp;
  }
  return day
    + sumres
    + (365 * (year - 1))
    + quotient(year, 4)
    + BEFORE_COPTIC;
}

void
rd_to_coptic(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, month, day, year;
  int sumres1, sumres2;

  approx = approximate(date - BEFORE_COPTIC, 366);
  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= coptic_to_rd(1 + y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > coptic_to_rd
	  (year, m, coptic_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date - (coptic_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
ethiopian_leap_year(int year)
{
  return coptic_leap_year(year);
}

int
ethiopian_last_day_of_month(int year, int month)
{
  return coptic_last_day_of_month(year, month);
}

#define EPOCH_ETHIOPIAN 2796
#define BEFORE_ETHIOPIAN (2796 - 1)

int
ethiopian_to_rd(int year, int month, int day)
{
  return
    coptic_to_rd(year, month, day) - (EPOCH_COPTIC - EPOCH_ETHIOPIAN);
}

void
rd_to_ethiopian(int date, int *ryear, int *rmonth, int *rday)
{
  rd_to_coptic
    (date + (EPOCH_COPTIC - EPOCH_ETHIOPIAN),
     ryear, rmonth, rday);
}

int
jalali_leap_year(int year)
{
    return mod(29 + (8 * year), 33) < 8;
}

int
jalali_last_day_of_month(int year, int month)
{
  if (month == 12 && jalali_leap_year(year))
      return 30;
  switch (month) {
  case  1: return 31;
  case  2: return 31;
  case  3: return 31;
  case  4: return 31;
  case  5: return 31;
  case  6: return 31;
  case  7: return 30;
  case  8: return 30;
  case  9: return 30;
  case 10: return 30;
  case 11: return 30;
  case 12: return 29;
  default: return 0;
  }
}

#define BEFORE_JALALI (226895 - 1)

int
jalali_to_rd(int year, int month, int day)
{
  int sumres;

  {
    int temp, m;
    for (temp = 0, m = 1;
	 (m < month);
	 temp = temp + jalali_last_day_of_month(year, m), m++)
      ;
    sumres = temp;
  }
  return day
    + sumres
    + (365 * (year - 1))
    + quotient(21 + (8 * year), 33)
    + BEFORE_JALALI;
}

void
rd_to_jalali(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, month, day, year;
  int sumres1, sumres2;

  approx = approximate(date - BEFORE_JALALI, 366);
  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= jalali_to_rd(1 + y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > jalali_to_rd
	  (year, m, jalali_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date - (jalali_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
bahai_leap_year(int year)
{
    return gregorian_leap_year(year + 1844);
}

int
bahai_last_day_of_month(int year, int month)
{
  if (month == 19) {
    if (bahai_leap_year(year))
      return 5;
    else
      return 4;
  }
  return 19;
}

#define BEFORE_BAHAI (673222 - 1)

int
bahai_to_rd(int year, int month, int day)
{
  int sumres;

  {
    int temp, m;
    for (temp = 0, m = 1;
	 (m < month);
	 temp = temp + bahai_last_day_of_month(year, m), m++)
      ;
    sumres = temp;
  }
  return day
    + sumres
    + gregorian_to_rd(year + 1843, 3, 20);
}

void
rd_to_bahai(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, month, day, year;
  int sumres1, sumres2;

  approx = approximate(date - BEFORE_BAHAI, 366);
  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= bahai_to_rd(1 + y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > bahai_to_rd
	  (year, m, bahai_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date - (bahai_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

void
bahai_year_to_vahid(int year, int *rkull, int *rvahid, int *ryear)
{
  int r;
  *rkull = quotient(year - 1,  361) + 1;
  r = mod(year - 1, 361);
  *rvahid = quotient(r, 19) + 1;
  *ryear = mod(r, 19) + 1;
}

int
bahai_vahid_to_year(int kull, int vahid, int year)
{
  return (kull - 1) * 361 + (vahid - 1) * 19 + year;
}

int
indian_national_leap_year(int year)
{
    return gregorian_leap_year(year + 78);
}

int
indian_national_last_day_of_month(int year, int month)
{
  if (month == 1 && indian_national_leap_year(year))
      return 31;
  switch (month) {
  case  1: return 30;
  case  2: return 31;
  case  3: return 31;
  case  4: return 31;
  case  5: return 31;
  case  6: return 31;
  case  7: return 30;
  case  8: return 30;
  case  9: return 30;
  case 10: return 30;
  case 11: return 30;
  case 12: return 30;
  default: return 0;
  }
}

int
indian_national_to_rd(int year, int month, int day)
{
  int sumres;

  {
    int temp, m;
    for (temp = 0, m = 1;
	 (m < month);
	 temp = temp + indian_national_last_day_of_month(year, m), m++)
      ;
    sumres = temp;
  }
  return day
    + sumres
    + gregorian_to_rd(year + 78, 1, 1) + 79;
}

#define BEFORE_INDIAN_NATIONAL (28205 - 1)

void
rd_to_indian_national(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, month, day, year;
  int sumres1, sumres2;

  approx = approximate(date - BEFORE_INDIAN_NATIONAL, 366);
  {
    int temp, y;
    for (temp = -1, y = approx;
	 (date >= indian_national_to_rd(y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > indian_national_to_rd
	  (year, m, indian_national_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date - (indian_national_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
bengali_leap_year(int year)
{
    return gregorian_leap_year(year + 594);
}

int
bengali_last_day_of_month(int year, int month)
{
  if (month == 11 && bengali_leap_year(year))
      return 31;
  switch (month) {
  case  1: return 31;
  case  2: return 31;
  case  3: return 31;
  case  4: return 31;
  case  5: return 31;
  case  6: return 30;
  case  7: return 30;
  case  8: return 30;
  case  9: return 30;
  case 10: return 30;
  case 11: return 30;
  case 12: return 30;
  default: return 0;
  }
}

int
bengali_to_rd(int year, int month, int day)
{
  int sumres;

  {
    int temp, m;
    for (temp = 0, m = 1;
	 (m < month);
	 temp = temp + bengali_last_day_of_month(year, m), m++)
      ;
    sumres = temp;
  }
  return day
    + sumres
    + gregorian_to_rd(year + 593, 4, 13);
}

#define BEFORE_BENGALI (216693 - 1)

void
rd_to_bengali(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, month, day, year;
  int sumres1, sumres2;

  approx = approximate(date - BEFORE_BENGALI, 366);
  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= bengali_to_rd(1 + y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > bengali_to_rd
	  (year, m, bengali_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date - (bengali_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
nanakshahi_leap_year(int year)
{
    return gregorian_leap_year(year + 1469);
}

int
nanakshahi_last_day_of_month(int year, int month)
{
  if (month == 12 && nanakshahi_leap_year(year))
      return 31;
  switch (month) {
  case  1: return 31;
  case  2: return 31;
  case  3: return 31;
  case  4: return 31;
  case  5: return 31;
  case  6: return 30;
  case  7: return 30;
  case  8: return 30;
  case  9: return 30;
  case 10: return 30;
  case 11: return 30;
  case 12: return 30;
  default: return 0;
  }
}

int
nanakshahi_to_rd(int year, int month, int day)
{
  int sumres;

  {
    int temp, m;
    for (temp = 0, m = 1;
	 (m < month);
	 temp = temp + nanakshahi_last_day_of_month(year, m), m++)
      ;
    sumres = temp;
  }
  return day
    + sumres
    + gregorian_to_rd(year + 1468, 3, 13);
}

#define BEFORE_NANAKSHAHI (536258 - 1)

void
rd_to_nanakshahi(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, month, day, year;
  int sumres1, sumres2;

  approx = approximate(date - BEFORE_NANAKSHAHI, 366);
  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= nanakshahi_to_rd(1 + y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > nanakshahi_to_rd
	  (year, m, nanakshahi_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date - (nanakshahi_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

#ifndef PLUTO
int
ordinal_to_rd(int year, int day)
{
  return gregorian_to_rd(year, 1, 1) + day - 1;
}

void
rd_to_ordinal(int date, int *ryear, int *rday)
{
  int month, day, year, date2;

  rd_to_gregorian(date, &year, &month, &day);
  date2 = gregorian_to_rd(year, 1, 1);
  if (rday)
    *rday = date - date2 + 1;
  if (ryear)
    *ryear = year;
}
#endif

int
jd_to_rd(int date) /* chronological */
{
  return date - 1721425;
}

int
rd_to_jd(int date) /* chronological */
{
  return date + 1721425;
}

#ifndef PLUTO
int
mjd_to_rd(int date) /* chronological */
{
  return date + 678576;
}

int
rd_to_mjd(int date) /* chronological */
{
  return date - 678576;
}

int
mjd_to_jd(int date) /* chronological */
{
  return date + 2400001;
}

int
jd_to_mjd(int date) /* chronological */
{
  return date - 2400001;
}

int
ld_to_rd(int date)
{
  return date + 577735;
}

int
rd_to_ld(int date)
{
  return date - 577735;
}

int
rd_to_day_of_week(int date)
{
  return mod(date, 7);
}
#endif /* not PLUTO */


/*
Local Variables:
c-basic-offset: 2
End:
*/
