/*
  calendrical.c: Translated by Tadayoshi Funaba 1996-2001,2014

  The original Common Lisp code is from ``Calendrical
  Calculations'' by Nachum Dershowitz and Edward
  M. Reingold, Software---Practice & Experience,
  vol. 20, no. 9 (September, 1990), pp. 899--928 and
  from ``Calendrical Calculations, II: Three Historical
  Calendars'' by Edward M. Reingold, Nachum Dershowitz,
  and Stewart M. Clamen, Software---Practice & Experience,
  vol. 23, no. 4 (April, 1993), pp. 383--404.

  This code is in the public domain, but any use of it
  should publically acknowledge its source.

  $Id: calendrical.c,v 1.9 2014-04-08 19:27:31+09 tadf Exp $
*/

#define MODULE

#ifndef NULL
#define NULL 0
#endif

#include <stdlib.h>
#include <math.h>
#include "calendrical.h"

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
gregorian_leap_year(int year)
{
  return
    mod(year, 4) == 0 &&
    !(mod(year, 400) == 100 ||
      mod(year, 400) == 200 ||
      mod(year, 400) == 300);
}

int
gregorian_last_day_of_month(int year, int month)
{
  if (month == 2 && gregorian_leap_year(year))
    return 29;
  switch (month) {
  case  1: return 31;
  case  2: return 28;
  case  3: return 31;
  case  4: return 30;
  case  5: return 31;
  case  6: return 30;
  case  7: return 31;
  case  8: return 31;
  case  9: return 30;
  case 10: return 31;
  case 11: return 30;
  case 12: return 31;
  default: return 0;
  }
}

int
gregorian_to_rd(int year, int month, int day)
{
  int sumres;

  {
    int temp, m;
    for (temp = 0, m = 1;
	 (m < month);
	 temp = temp + gregorian_last_day_of_month(year, m), m++)
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
rd_to_gregorian(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, month, day, year;
  int sumres1, sumres2;

#ifndef PAPER
  approx = approximate(date, 366);
#else
  approx = quotient(date, 366);
#endif
  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= gregorian_to_rd(1 + y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > gregorian_to_rd
	  (year, m, gregorian_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date
    - (gregorian_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
kday_on_or_before(int date, int k)
{
  return date - mod(date - k, 7);
}

int
iso_to_rd(int year, int week, int day)
{
  return kday_on_or_before(gregorian_to_rd(year, 1, 4), 1)
    + (7 * (week - 1))
    + (day - 1);
}

void
rd_to_iso(int date, int *ryear, int *rweek, int *rday)
{
  int approx, week, day, year;

  rd_to_gregorian(date - 3, &approx, NULL, NULL);
  year = (date >= iso_to_rd(1 + approx, 1, 1)) ?
    1 + approx : approx;
  week = 1 + quotient(date - iso_to_rd(year, 1, 1), 7);
  day = (mod(date, 7) == 0) ?
    7 : mod(date, 7);
  if (rweek)
    *rweek = week;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
julian_leap_year(int year)
{
#if !defined(PAPER) && defined(OMIT_LEAP4)
  return year != 4 && mod(year, 4) == 0;
#else
  return mod(year, 4) == 0;
#endif
}

int
julian_last_day_of_month(int year, int month)
{
  if (month == 2 && julian_leap_year(year))
    return 29;
  switch (month) {
  case  1: return 31;
  case  2: return 28;
  case  3: return 31;
  case  4: return 30;
  case  5: return 31;
  case  6: return 30;
  case  7: return 31;
  case  8: return 31;
  case  9: return 30;
  case 10: return 31;
  case 11: return 30;
  case 12: return 31;
  default: return 0;
  }
}

int
julian_to_rd(int year, int month, int day)
{
  int sumres;

  {
    int temp, m;
    for (temp = 0, m = 1;
	 (m < month);
	 temp = temp + julian_last_day_of_month(year, m), m++)
      ;
    sumres = temp;
  }
  return day
    + sumres
    + (365 * (year - 1))
    + quotient(year - 1, 4)
#if !defined(PAPER) && defined(OMIT_LEAP4)
    - ((year > 4) ? 2 : 1);
#else
    - 2;
#endif
}

void
rd_to_julian(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, month, day, year;
  int sumres1, sumres2;

#if !defined(PAPER) && defined(OMIT_LEAP4)
  approx = approximate(date + 1, 366);
#elif !defined(PAPER)
  approx = approximate(date + 2, 366);
#else
  approx = quotient(date + 2, 366);
#endif

  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= julian_to_rd(1 + y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > julian_to_rd
	  (year, m, julian_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date - (julian_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
islamic_leap_year(int year)
{
  return mod(14 + (11 * year), 30) < 11;
}

int
islamic_last_day_of_month(int year, int month)
{
  return (oddp (month) ||
	  ((month == 12) && islamic_leap_year(year))) ?
    30 : 29;
}

int
islamic_to_rd(int year, int month, int day)
{
  return day
    + (29 * (month - 1))
    + quotient(month, 2)
    + ((year - 1) * 354)
    + quotient(3 + (11 * year), 30)
    + 227014;
}

void
rd_to_islamic(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, month, day, year;
  int sumres1, sumres2;

#ifdef PAPER
  if (date <= 227014) {
    if (rmonth)
      *rmonth = 0;
    if (rday)
      *rday = 0;
    if (ryear)
      *ryear = 0;
    return;
  }
#endif
#ifndef PAPER
  approx = approximate(date - 227014, 355);
#else
  approx = quotient(date - 227014, 355);
#endif
  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= islamic_to_rd(1 + y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > islamic_to_rd
	  (year, m, islamic_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date
    - (islamic_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
hebrew_leap_year(int year)
{
  return mod(1 + (7 * year), 19) < 7;
}

int
hebrew_last_month_of_year(int year)
{
  return (hebrew_leap_year(year)) ?
    13 : 12;
}

int
hebrew_last_day_of_month(int year, int month)
{
  return
    ((month == 2 ||
      month == 4 ||
      month == 6 ||
      month == 10 ||
      month == 13) ||
     (month == 12 && !hebrew_leap_year(year)) ||
     (month == 8 && !long_heshvan(year)) ||
     (month == 9 && short_kislev(year))) ?
    29 : 30;
}

int
hebrew_calendar_elapsed_days(int year)
{
  int months_elapsed, parts_elapsed, hours_elapsed,
    day, parts, alternative_day;

  months_elapsed = (235 * quotient(year - 1, 19))
    + (12 * mod(year - 1, 19))
    + quotient(1 + (7 * mod (year - 1, 19)), 19);
  parts_elapsed = 204
    + (793 * mod(months_elapsed, 1080));
  hours_elapsed = 5
    + (12 * months_elapsed)
    + (793 * quotient(months_elapsed, 1080))
    + quotient(parts_elapsed, 1080);
  day = 1
    + (29 * months_elapsed)
    + quotient(hours_elapsed, 24);
  parts = (1080 * mod(hours_elapsed, 24))
    + mod(parts_elapsed, 1080);
  alternative_day =
    ((parts >= 19440) ||
     ((mod(day, 7) == 2) && (parts >= 9924)
      && !hebrew_leap_year(year)) ||
     ((mod(day, 7) == 1) && (parts >= 16789)
      && hebrew_leap_year(year - 1))) ?
    1 + day : day;
  return ((mod (alternative_day, 7) == 0) ||
	  (mod(alternative_day, 7) == 3) ||
	  (mod(alternative_day, 7) == 5)) ?
    1 + alternative_day : alternative_day;
}

int
hebrew_days_in_year(int year)
{
  return
    hebrew_calendar_elapsed_days(1 + year)
    - hebrew_calendar_elapsed_days(year);
}

int
long_heshvan(int year)
{
  return mod(hebrew_days_in_year(year), 10) == 5;
}

int
short_kislev(int year)
{
  return mod(hebrew_days_in_year (year), 10) == 3;
}

int
hebrew_to_rd(int year, int month, int day)
{
  if (month < 7) {
    int sumres1, sumres2;

    {
      int temp, m;
      for (temp = 0, m = 7;
	   (m <= hebrew_last_month_of_year(year));
	   temp = temp + hebrew_last_day_of_month(year, m), m++)
	;
      sumres1 = temp;
    }
    {
      int temp, m;
      for (temp = 0, m = 1;
	   (m < month);
	   temp = temp + hebrew_last_day_of_month(year, m), m++)
	;
      sumres2 = temp;
    }
    return day
      + sumres1
      + sumres2
      + hebrew_calendar_elapsed_days(year)
      - 1373429;
  } else {
    int sumres;

    {
      int temp, m;
      for (temp = 0, m = 7;
	   (m < month);
	   temp = temp + hebrew_last_day_of_month(year, m), m++)
	;
      sumres = temp;
    }
    return day
      + sumres
      + hebrew_calendar_elapsed_days(year)
      - 1373429;
  }
}

void
rd_to_hebrew(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, year, start, month, day;
  int sumres1, sumres2;

#ifndef PAPER
  approx = approximate(date + 1373429, 366);
#else
  approx = quotient(date + 1373429, 366);
#endif
  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= hebrew_to_rd(1 + y, 7, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  start = (date < hebrew_to_rd(year, 1, 1)) ?
    7 : 1;
  {
    int temp, m;
    for (temp = 0, m = start;
	 (date > hebrew_to_rd
	  (year, m, hebrew_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = start
    + sumres2;
  day = date
    - (hebrew_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

#if !defined(PLUTO) && !defined(MODULE)
int
independence_day(int year)
{
  return gregorian_to_rd(year, 7, 4);
}
#endif

#ifndef PLUTO
int
nth_kday(int year, int month, int n, int k)
{
  if (n > 0)
    return
      kday_on_or_before
      (gregorian_to_rd(year, month, 7), k)
      + (7 * (n - 1));
  return
    kday_on_or_before
    (gregorian_to_rd
     (year, month,
      gregorian_last_day_of_month(year, month)),
     k)
    + (7 * (1 + n));
}
#endif

#if !defined(PLUTO) && !defined(MODULE)
int
labor_day(int year)
{
  return Nth_Kday(1, 1, 9, year);
}

int
memorial_day(int year)
{
  return Nth_Kday(-1, 1, 5, year);
}

int
daylight_savings_start(int year)
{
  return Nth_Kday(1, 0, 4, year);
}

int
daylight_savings_end(int year)
{
  return Nth_Kday(-1, 0, 10, year);
}

int
christmas(int year)
{
  return gregorian_to_rd(year, 12, 25);
}

int
advent(int year)
{
  return kday_on_or_before(gregorian_to_rd(year, 12, 3), 0);
}

int
epiphany(int year)
{
  return 12 + christmas(year);
}

int
eastern_orthodox_christmas(int year)
{
  int jan1, dec31, y, c1, c2;

  jan1 = gregorian_to_rd(year, 1, 1);
  dec31 = gregorian_to_rd(year, 12, 31);
  rd_to_julian(jan1, &y, NULL, NULL);
  c1 = julian_to_rd(y, 12, 25);
  c2 = julian_to_rd(1 + y, 12, 25);
  if (jan1 <= c1 && c1 <= dec31)
    return c1;
  else if (jan1 <= c2 && c2 <= dec31)
    return c2;
  return 0;
}
#endif /* not PLUTO and not MODULE */

int
nicaean_rule_easter(int year)
{
  int shifted_epact, paschal_moon;

  shifted_epact = mod(14 + (11 * mod(year, 19)), 30);
  paschal_moon = julian_to_rd(year, 4, 19)
    - shifted_epact;
  return kday_on_or_before(paschal_moon + 7, 0);
}

int
easter(int year)
{
  int century, shifted_epact, adjusted_epact, paschal_moon;

  century = 1 + quotient(year, 100);
  shifted_epact = mod(14 + (11 * mod(year, 19))
		       - quotient(3 * century, 4)
		       + quotient(5 + (8 * century), 25)
		       + (30 * century),
		       30);
  adjusted_epact = ((shifted_epact == 0)
		    || ((shifted_epact == 1) && (10 < mod(year, 19)))) ?
    1 + shifted_epact : shifted_epact;
  paschal_moon = gregorian_to_rd(year, 4, 19)
    - adjusted_epact;
  return kday_on_or_before(paschal_moon + 7, 0);
}

#if !defined(PLUTO) && !defined(MODULE)
int
pentecost(int year)
{
  return 49 + easter(year);
}

void
islamic_date(int year, int month, int day, int date[3])
{
  int jan1, dec31, y, date1, date2, date3;

  jan1 = gregorian_to_rd(year, 1, 1);
  dec31 = gregorian_to_rd(year, 12, 31);
  rd_to_islamic(jan1, &y, NULL, NULL);
  date1 = islamic_to_rd(y, month, day);
  date2 = islamic_to_rd(1 + y, month, day);
  date3 = islamic_to_rd(2 + y, month, day);
  date[0] = (jan1 <= date1 && date1 <= dec31) ?
    date1 : 0;
  date[1] = (jan1 <= date2 && date2 <= dec31) ?
    date2 : 0;
  date[2] = (jan1 <= date3 && date3 <= dec31) ?
    date3 : 0;
}

void
mulad_al_nabi(int year, int date[3])
{
  islamic_date(year, 3, 12, date);
}

int
yom_kippur(int year)
{
  return hebrew_to_rd(year + 3761, 7, 10);
}

int
passover(int year)
{
  return hebrew_to_rd(year + 3760, 1, 15);
}

int
purim(int year)
{
  return
    hebrew_to_rd
    (year + 3760,
     hebrew_last_month_of_year(year + 3760), 14);
}

int
ta_anit_esther(int year)
{
  int purim_date;

  purim_date = purim(year);
  return (mod(purim_date, 7) == 0) ?
    purim_date - 3 : purim_date - 1;
}

int
tisha_b_av(int year)
{
  int ninth_of_av;

  ninth_of_av = hebrew_to_rd(year + 3760, 5, 9);
  return (mod(ninth_of_av, 7) == 6) ?
    1 + ninth_of_av : ninth_of_av;
}

int
hebrew_birthday(int birth_year, int birth_month, int birth_day, int year)
{
  return
    (birth_month == hebrew_last_month_of_year(birth_year)) ?
    hebrew_to_rd(year, hebrew_last_month_of_year(year), birth_day) :
    hebrew_to_rd(year, birth_month, birth_day);
}

int
yahrzeit(int death_year, int death_month, int death_day, int year)
{
  if (death_month == 8 &&
      death_day == 30 &&
      !long_heshvan(1 + death_year))
    return hebrew_to_rd(year, 9, 1) - 1;
  if (death_month == 9 &&
      death_day == 30 &&
      !short_kislev(1 + death_year))
    return hebrew_to_rd(year, 10, 1) - 1;
  if (death_month == 13)
    return hebrew_to_rd
      (year, hebrew_last_month_of_year(year), death_day);
  if (death_day == 30 &&
      death_month == 12 &&
      !hebrew_leap_year(year))
    return hebrew_to_rd(year, 11, 30);
  return hebrew_to_rd(year, death_month, death_day);
}
#endif /* not PLUTO and not MODULE */

#ifndef SPINDEN_CORRELATION
#ifndef PAPER
/* GMT - Sept 6, 3114 BCE (Julian) */
#define mayan_days_before_absolute_zero 1137142
#else
/* GMT - Sept 8, 3114 BCE (Julian) */
#define mayan_days_before_absolute_zero 1137140
#endif
#else
/* SPINDEN - Nov 11, 3374 BCE (Julian) */
#define mayan_days_before_absolute_zero 1232041
#endif

int
mayan_long_count_to_rd(int baktun, int katun, int tun, int uinal, int kin)
{
  return baktun * 144000
    + katun * 7200
    + tun * 360
    + uinal * 20
    + kin
    - mayan_days_before_absolute_zero;
}

void
rd_to_mayan_long_count
(int date, int *rbaktun, int *rkatun, int *rtun, int *ruinal, int *rkin)
{
  int long_count,
    baktun, day_of_baktun,
    katun, day_of_katun,
    tun, day_of_tun,
    uinal, kin;

  long_count = date + mayan_days_before_absolute_zero;
  baktun = quotient(long_count, 144000);
  day_of_baktun = mod(long_count, 144000);
  katun = quotient(day_of_baktun, 7200);
  day_of_katun = mod(day_of_baktun, 7200);
  tun = quotient(day_of_katun, 360);
  day_of_tun = mod(day_of_katun, 360);
  uinal = quotient(day_of_tun, 20);
  kin = mod(day_of_tun, 20);
  if (rbaktun)
    *rbaktun = baktun;
  if (rkatun)
    *rkatun = katun;
  if (rtun)
    *rtun = tun;
  if (ruinal)
    *ruinal = uinal;
  if (rkin)
    *rkin = kin;
}

#define mayan_haab_at_epoch_day 8
#define mayan_haab_at_epoch_month 18

void
rd_to_mayan_haab(int date, int *rmonth, int *rday)
{
  int long_count, day_of_haab, day, month;

  long_count = date + mayan_days_before_absolute_zero;
  day_of_haab = mod
    (long_count
     + mayan_haab_at_epoch_day
     + (20 * (mayan_haab_at_epoch_month - 1)),
     365);
  day = mod(day_of_haab, 20);
  month = 1 + quotient(day_of_haab, 20);
  if (rday)
    *rday = day;
  if (rmonth)
    *rmonth = month;
}

int
mayan_haab_difference(int month1, int day1, int month2, int day2)
{
  return mod((20 * (month2 - month1))
	      + (day2 - day1),
	      365);
}

int
mayan_haab_on_or_before(int haab_month, int haab_day, int date)
{
  int zero_day, zero_month;

  rd_to_mayan_haab(0, &zero_month, &zero_day);
  return date
    - mod(date
	  - mayan_haab_difference
	  (zero_month, zero_day, haab_month, haab_day),
	  365);
}

static int
adjusted_mod(int m, int n)
{
  return 1 + mod(m - 1, n);
}

#define mayan_tzolkin_at_epoch_number 4
#define mayan_tzolkin_at_epoch_name 20

void
rd_to_mayan_tzolkin(int date, int *rname, int *rnumber)
{
  int long_count, number, name;

  long_count = date + mayan_days_before_absolute_zero;
  number = adjusted_mod(long_count + mayan_tzolkin_at_epoch_number,
			 13);
  name = adjusted_mod(long_count + mayan_tzolkin_at_epoch_name,
		       20);
  if (rnumber)
    *rnumber = number;
  if (rname)
    *rname = name;
}

int
mayan_tzolkin_difference(int name1, int number1, int name2, int number2)
{
  int number_difference, name_difference;

  number_difference = number2 - number1;
  name_difference = name2 - name1;
  return mod(number_difference
	     + (13 * mod(3 * (number_difference - name_difference),
			 20)),
	     260);
}

int
mayan_tzolkin_on_or_before(int name, int number, int date)
{
  int zero_number, zero_name;

  rd_to_mayan_tzolkin(0, &zero_name, &zero_number);
  return date
    - mod(date
	  - mayan_tzolkin_difference
	  (zero_name, zero_number, name, number),
	  260);
}

int
mayan_haab_tzolkin_on_or_before
(int month, int day, int name, int number, int date)
{
  int zero_day, zero_month, zero_number, zero_name,
    haab_difference, tzolkin_difference, difference;

  rd_to_mayan_haab(0, &zero_month, &zero_day);
  haab_difference = mayan_haab_difference(zero_month, zero_day, month, day);
  rd_to_mayan_tzolkin(0, &zero_name, &zero_number);
  tzolkin_difference = mayan_tzolkin_difference(zero_name, zero_number, name, number);
  difference = tzolkin_difference - haab_difference;
  if (mod(difference, 5) == 0)
    return date
      - mod(date
	     - (haab_difference + (365 * difference)),
	     18980);
  return 0;
}

int
french_leap_year(int year)
{
  return
    (year == 3 ||
     year == 7 ||
     year == 11) ||
    (year == 15 ||
     year == 20) ||
#ifndef PAPER
    (((year > 20) || (year < 0)) &&
#else
    (year > 20 &&
#endif
     (0 == mod(year, 4)) &&
     !((mod(year, 400) == 100) ||
       (mod(year, 400) == 200) ||
       (mod(year, 400) == 300)) &&
     !(0 == mod(year, 4000)));
}

int
french_last_day_of_month(int year, int month)
{
  if (month < 13)
    return 30;
  else if (french_leap_year(year))
    return 6;
  return 5;
}

int
french_to_rd(int year, int month, int day)
{
  return 654414
    + (365 * (year - 1))
#ifndef PAPER
    + (((year < 20)) && (year > 0) ?
#else
    + ((year < 20) ?
#endif
       (quotient(year, 4)) :
       (quotient(year - 1, 4)
	- quotient(year - 1, 100)
	+ quotient(year - 1, 400)
	- quotient(year - 1, 4000)))
    + (30 * (month - 1))
    + day;
}

void
rd_to_french(int date, int *ryear, int *rmonth, int *rday)
{
  int approx, year, month, day;
  int sumres1, sumres2;

#ifdef PAPER
  if (date < 654415) {
    if (rmonth)
      *rmonth = 0;
    if (rday)
      *rday = 0;
    if (ryear)
      *ryear = 0;
    return;
  }
#endif
#ifndef PAPER
  approx = approximate(date - 654414, 366);
#else
  approx = quotient(date - 654414, 366);
#endif
  {
    int temp, y;
    for (temp = 0, y = approx;
	 (date >= french_to_rd(1 + y, 1, 1));
	 temp = temp + 1, y++)
      ;
    sumres1 = temp;
  }
  year = approx
    + sumres1;
  {
    int temp, m;
    for (temp = 0, m = 1;
	 (date > french_to_rd
	  (year, m, french_last_day_of_month(year, m)));
	 temp = temp + 1, m++)
      ;
    sumres2 = temp;
  }
  month = 1
    + sumres2;
  day = date - (french_to_rd(year, month, 1) - 1);
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

#undef quotient
#define quotient(m, n) (floor(((double)(m)) / ((double)(n))))
#undef mod
#define mod(m, n) f_mod(m, n)
static double
f_mod(double m, double n)
{
  double x;

  x = fmod(m, n);
  if ((n < 0) ? (x > 0) : (x < 0))
    x += n;
  return x;
}
#undef oddp
#define oddp(n) (((int)(n)) % 2)

#define solar_sidereal_year (365 + 279457.0 / 1080000)
#define solar_month (solar_sidereal_year / 12)
#define lunar_sidereal_month (27 + 4644439.0 / 14438334)
#define lunar_synodic_month (29 + 7087771.0 / 13358334)

double
solar_longitude(double days)
{
  return mod(days / solar_sidereal_year, 1) * 360;
}

double
zodiac(double days)
{
  return 1 + quotient(solar_longitude(days), 30);
}

void
rd_to_old_hindu_solar(int date, int *ryear, int *rmonth, int *rday)
{
  double hdate;
  int year, month, day;

  hdate = date + 1132959 + 1.0 / 4;
  year = quotient(hdate, solar_sidereal_year);
  month = zodiac(hdate);
  day = 1 + floor(mod(hdate, solar_month));
  if (rmonth)
    *rmonth = month;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
old_hindu_solar_to_rd(int year, int month, int day)
{
  return floor((year * solar_sidereal_year)
		+ ((month - 1) * solar_month)
		+ day - 1.0 / 4
		- 1132959);
}

double
lunar_longitude(double days)
{
  return mod(days / lunar_sidereal_month, 1) * 360;
}

double
lunar_phase(double days)
{
  return 1
    + quotient
    (mod(lunar_longitude(days) - solar_longitude(days),
	 360),
     12);
}

double
new_moon(double days)
{
  return days - mod(days, lunar_synodic_month);
}

void
rd_to_old_hindu_lunar
(int date, int *ryear, int *rmonth, int *rleapmonth, int *rday)
{
  double hdate, sunrise, last_new_moon, next_new_moon, next_month;
  int day, month, leapmonth, year;

  hdate = date + 1132959;
  sunrise = hdate + 1.0 / 4;
  last_new_moon = new_moon(sunrise);
  next_new_moon = last_new_moon + lunar_synodic_month;
  day = lunar_phase(sunrise);
  month = adjusted_mod(1 + zodiac (last_new_moon), 12);
  leapmonth = zodiac(last_new_moon) == zodiac (next_new_moon);
  next_month = next_new_moon + (leapmonth ? lunar_synodic_month : 0);
  year = quotient(next_month, solar_sidereal_year);
  if (rmonth)
    *rmonth = month;
  if (rleapmonth)
    *rleapmonth = leapmonth;
  if (rday)
    *rday = day;
  if (ryear)
    *ryear = year;
}

int
old_hindu_lunar_precedes
  (int year1, int month1, int leap1, int day1,
   int year2, int month2, int leap2, int day2)
{
  return ((year1 < year2) ||
	  ((year1 == year2) &&
	   ((month1 < month2) ||
	    ((month1 == month2) &&
	     ((leap1 && !leap2) ||
	      ((leap1 == leap2) &&
	       (day1 < day2)))))));
}

int
old_hindu_lunar_to_rd(int year, int month, int leapmonth, int day)
{
  int years, months, approx, try,
    month1, leapmonth1, day1, year1;
  int sumres;

  years = year;
  months = month - 2;
  approx = floor(years * solar_sidereal_year)
    + floor(months * lunar_synodic_month)
    - 1132959;
  {
    int temp, i;
    for (temp = 0, i = approx;
	 (rd_to_old_hindu_lunar
	  (i, &year1, &month1, &leapmonth1, &day1),
	  old_hindu_lunar_precedes
	  (year1, month1, leapmonth1, day1,
	   year, month, leapmonth, day));
	 temp = temp + 1, i++)
      ;
    sumres = temp;
  }
  try = approx
    + sumres;
  rd_to_old_hindu_lunar(try, &year, &month1, &leapmonth1, &day1);
  if (month1 == month &&
      leapmonth1 == leapmonth &&
      day1 == day &&
      year1 == year)
    return try;
  return 0;
}


/*
Local Variables:
c-basic-offset: 2
End:
*/
