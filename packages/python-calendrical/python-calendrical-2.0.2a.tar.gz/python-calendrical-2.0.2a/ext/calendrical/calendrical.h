/*
  calendrical.h: Written by Tadayoshi Funaba 1997-2000,2014

  This code is in the public domain, but any use of it
  should publically acknowledge its source.

  $Id: calendrical.h,v 1.6 2014-04-08 19:27:31+09 tadf Exp $
*/

#if !defined(__GNUC__) \
 || !( __GNUC__ > 2 || (__GNUC__ == 2 && __GNUC_MINOR__ >= 6))
#undef __attribute__
#define __attribute__(x)
#endif

extern int gregorian_leap_year(int year) __attribute__ ((const));
extern int gregorian_last_day_of_month(int year, int month) __attribute__ ((const));
extern int gregorian_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_gregorian(int date, int *ryear, int *rmonth, int *rday);
extern int kday_on_or_before(int date, int k) __attribute__ ((const));
extern int iso_to_rd(int year, int week, int day) __attribute__ ((const));
extern void rd_to_iso(int date, int *ryear, int *rweek, int *rday);
extern int julian_leap_year(int year) __attribute__ ((const));
extern int julian_last_day_of_month(int year, int month) __attribute__ ((const));
extern int julian_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_julian(int date, int *ryear, int *rmonth, int *rday);
extern int islamic_leap_year(int year) __attribute__ ((const));
extern int islamic_last_day_of_month(int year, int month) __attribute__ ((const));
extern int islamic_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_islamic(int date, int *ryear, int *rmonth, int *rday);
extern int hebrew_leap_year(int year) __attribute__ ((const));
extern int hebrew_last_month_of_year(int year) __attribute__ ((const));
extern int hebrew_last_day_of_month(int year, int month) __attribute__ ((const));
extern int hebrew_calendar_elapsed_days(int year) __attribute__ ((const));
extern int hebrew_days_in_year(int year) __attribute__ ((const));
extern int long_heshvan(int year) __attribute__ ((const));
extern int short_kislev(int year) __attribute__ ((const));
extern int hebrew_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_hebrew(int date, int *ryear, int *rmonth, int *rday);
#if !defined(PLUTO) && !defined(MODULE)
extern int independence_day(int year) __attribute__ ((const));
#endif
#ifndef PLUTO
extern int nth_kday(int year, int month, int n, int k) __attribute__ ((const));
#endif
#if !defined(PLUTO) && !defined(MODULE)
extern int labor_day(int year) __attribute__ ((const));
extern int memorial_day(int year) __attribute__ ((const));
extern int daylight_savings_start(int year) __attribute__ ((const));
extern int daylight_savings_end(int year) __attribute__ ((const));
extern int christmas(int year) __attribute__ ((const));
extern int advent(int year) __attribute__ ((const));
extern int epiphany(int year) __attribute__ ((const));
extern int eastern_orthodox_christmas(int year) __attribute__ ((const));
#endif /* not PLUTO and not MODULE */
extern int nicaean_rule_easter(int year) __attribute__ ((const));
extern int easter(int year) __attribute__ ((const));
#if !defined(PLUTO) && !defined(MODULE)
extern int pentecost(int year) __attribute__ ((const));
extern void islamic_date(int year, int month, int day, int date[3]);
extern void mulad_al_nabi(int year, int date[3]);
extern int yom_kippur(int year) __attribute__ ((const));
extern int passover(int year) __attribute__ ((const));
extern int purim(int year) __attribute__ ((const));
extern int ta_anit_esther(int year) __attribute__ ((const));
extern int tisha_b_av(int year) __attribute__ ((const));
extern int hebrew_birthday(int birth_year, int birth_month, int birth_day, int year) __attribute__ ((const));
extern int yahrzeit(int death_year, int death_month, int death_day, int year) __attribute__ ((const));
#endif /* not PLUTO and not MODULE */
extern int mayan_long_count_to_rd(int baktun, int katun, int tun, int uinal, int kin) __attribute__ ((const));
extern void rd_to_mayan_long_count(int date, int *rbaktun, int *rkatun, int *rtun, int *ruinal, int *rkin);
extern void rd_to_mayan_haab(int date, int *rmonth, int *rday);
extern int mayan_haab_difference(int month1, int day1, int month2, int day2) __attribute__ ((const));
extern int mayan_haab_on_or_before(int haab_month, int haab_day, int date) __attribute__ ((const));
extern void rd_to_mayan_tzolkin(int date, int *rname, int *rnumber);
extern int mayan_tzolkin_difference(int name1, int number1, int name2, int number2) __attribute__ ((const));
extern int mayan_tzolkin_on_or_before(int name, int number, int date) __attribute__ ((const));
extern int mayan_haab_tzolkin_on_or_before(int month, int day, int name, int number, int date) __attribute__ ((const));
extern int french_leap_year(int year) __attribute__ ((const));
extern int french_last_day_of_month(int year, int month) __attribute__ ((const));
extern int french_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_french(int date, int *ryear, int *rmonth, int *rday);
extern double solar_longitude(double days) __attribute__ ((const));
extern double zodiac(double days) __attribute__ ((const));
extern void rd_to_old_hindu_solar(int date, int *ryear, int *rmonth, int *rday);
extern int old_hindu_solar_to_rd(int year, int month, int day) __attribute__ ((const));
extern double lunar_longitude(double days) __attribute__ ((const));
extern double lunar_phase(double days) __attribute__ ((const));
extern double new_moon(double days) __attribute__ ((const));
extern void rd_to_old_hindu_lunar(int date, int *ryear, int *rmonth, int *rleapmonth, int *rday);
extern int old_hindu_lunar_precedes(int year1, int month1, int leap1, int day1, int year2, int month2, int leap2, int day2) __attribute__ ((const));
extern int old_hindu_lunar_to_rd(int year, int month, int leapmonth, int day) __attribute__ ((const));


/*
Local Variables:
c-basic-offset: 2
End:
*/
