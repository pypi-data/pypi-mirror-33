/*
  calendrical2.h (beta): Written by Tadayoshi Funaba 1997,1999,2000,2002,2007,2014

  This code is in the public domain, but any use of it
  should publically acknowledge its source.

  $Id: calendrical2.h,v 1.8 2014-04-27 09:42:02+09 tadf Exp $
*/

#if !defined(__GNUC__) \
 || !( __GNUC__ > 2 || (__GNUC__ == 2 && __GNUC_MINOR__ >= 6))
#undef __attribute__
#define __attribute__(x)
#endif

extern int world_leap_year(int year) __attribute__ ((const));
extern int world_last_day_of_month(int year, int month) __attribute__ ((const));
extern int world_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_world(int date, int *ryear, int *rmonth, int *rday);
extern int rd_to_world_day_of_week(int date) __attribute__ ((const));
extern int coptic_leap_year(int year) __attribute__ ((const));
extern int coptic_last_day_of_month(int year, int month) __attribute__ ((const));
extern int coptic_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_coptic(int date, int *ryear, int *rmonth, int *rday);
extern int ethiopian_leap_year(int year) __attribute__ ((const));
extern int ethiopian_last_day_of_month(int year, int month) __attribute__ ((const));
extern int ethiopian_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_ethiopian(int date, int *ryear, int *rmonth, int *rday);
extern int jalali_leap_year(int year) __attribute__ ((const));
extern int jalali_last_day_of_month(int year, int month) __attribute__ ((const));
extern int jalali_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_jalali(int date, int *ryear, int *rmonth, int *rday);
extern int bahai_leap_year(int year) __attribute__ ((const));
extern int bahai_last_day_of_month(int year, int month) __attribute__ ((const));
extern int bahai_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_bahai(int date, int *ryear, int *rmonth, int *rday);
extern void bahai_year_to_vahid(int year, int *rkull, int *rvahid, int *ryear);
extern int bahai_vahid_to_year(int kull, int vahid, int year) __attribute__ ((const));
extern int indian_national_leap_year(int year) __attribute__ ((const));
extern int indian_national_last_day_of_month(int year, int month) __attribute__ ((const));
extern int indian_national_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_indian_national(int date, int *ryear, int *rmonth, int *rday);
extern int bengali_leap_year(int year) __attribute__ ((const));
extern int bengali_last_day_of_month(int year, int month) __attribute__ ((const));
extern int bengali_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_bengali(int date, int *ryear, int *rmonth, int *rday);
extern int nanakshahi_leap_year(int year) __attribute__ ((const));
extern int nanakshahi_last_day_of_month(int year, int month) __attribute__ ((const));
extern int nanakshahi_to_rd(int year, int month, int day) __attribute__ ((const));
extern void rd_to_nanakshahi(int date, int *ryear, int *rmonth, int *rday);
#ifndef PLUTO
extern int ordinal_to_rd(int year, int day) __attribute__ ((const));
extern void rd_to_ordinal(int date, int *ryear, int *rday);
#endif
extern int jd_to_rd(int date) __attribute__ ((const));
extern int rd_to_jd(int date) __attribute__ ((const));
#ifndef PLUTO
extern int mjd_to_rd(int date) __attribute__ ((const));
extern int rd_to_mjd(int date) __attribute__ ((const));
extern int jd_to_mjd(int date) __attribute__ ((const));
extern int mjd_to_jd(int date) __attribute__ ((const));
extern int ld_to_rd(int date) __attribute__ ((const));
extern int rd_to_ld(int date) __attribute__ ((const));
extern int rd_to_day_of_week(int date) __attribute__ ((const));
#endif /* not PLUTO */


/*
Local Variables:
c-basic-offset: 2
End:
*/
