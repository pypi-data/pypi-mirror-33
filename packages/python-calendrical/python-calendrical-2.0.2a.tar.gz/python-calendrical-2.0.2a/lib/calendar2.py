import calendrical

def _get1_(x):
  try:
    ((a,),) = x
  except:
    (a,) = x
  return a

def _get3_(x):
  try:
    ((a, b, c),) = x
  except:
    (a, b, c) = x
  return a, b, c

def _get22_(x):
  try:
    ((a, b), (c, d),) = x
  except:
    (a, b, c, d) = x
  return a, b, c, d

def _get21_(x):
  try:
    ((a, b), c,) = x
  except:
    (a, b, c) = x
  return a, b, c

def _get221_(x):
  try:
    ((a, b), (c, d), e) = x
  except:
    (a, b, c, d, e) = x
  return a, b, c, d, e

def _get44_(x):
  try:
    ((a, b, c, d), (e, f, g, h),) = x
  except:
    (a, b, c, d, e, f, g, h) = x
  return a, b, c, d, e, f, g

def _get4_(x):
  try:
    ((a, b, c, d),) = x
  except:
    (a, b, c, d) = x
  return a, b, c, d

def _get2_(x):
  try:
    ((a, b),) = x
  except:
    (a, b) = x
  return a, b

def gregorian_leap_year(y):
  return calendrical.gregorian_leap_year(y)

def gregorian_last_day_of_month(m, y):
  return calendrical.gregorian_last_day_of_month(y, m)

def absolute_from_gregorian(*x):
  m, d, y = _get3_(x)
  return calendrical.gregorian_to_rd(y, m, d)

def gregorian_from_absolute(a):
  y, m, d = calendrical.rd_to_gregorian(a)
  return m, d, y

def Kday_on_or_before(a, k):
  return calendrical.kday_on_or_before(a, k)

def absolute_from_iso(*x):
  w, d, y = _get3_(x)
  return calendrical.iso_to_rd(y, w, d)

def iso_from_absolute(a):
  y, w, d = calendrical.rd_to_iso(a)
  return w, d, y

def absolute_from_calendar_week(*x):
  w, d, y = _get3_(x)
  return calendrical.iso_to_rd(y, w, d)

def calendar_week_from_absolute(a):
  y, w, d = calendrical.rd_to_iso(a)
  return w, d, y

def julian_leap_year(y):
  return calendrical.gregorian_leap_year(y)

def julian_last_day_of_month(m, y):
  return calendrical.julian_last_day_of_month(y, m)

def absolute_from_julian(*x):
  m, d, y = _get3_(x)
  return calendrical.julian_to_rd(y, m, d)

def julian_from_absolute(a):
  y, m, d = calendrical.rd_to_julian(a)
  return m, d, y

def islamic_leap_year(y):
  return calendrical.islamic_leap_year(y)

def islamic_last_day_of_month(m, y):
  return calendrical.islamic_last_day_of_month(y, m)

def absolute_from_islamic(*x):
  m, d, y = _get3_(x)
  return calendrical.islamic_to_rd(y, m, d)

def islamic_from_absolute(a):
  y, m, d = calendrical.rd_to_islamic(a)
  return m, d, y

def hebrew_leap_year(y):
  return calendrical.hebrew_leap_year(y)

def hebrew_last_month_of_year(y):
  return calendrical.hebrew_last_month_of_year(y)

def hebrew_last_day_of_month(m, y):
  return calendrical.hebrew_last_day_of_month(y, m)

def hebrew_calendar_elapsed_days(y):
  return calendrical.hebrew_calendar_elapsed_days(y)

def days_in_hebrew_year(y):
  return calendrical.hebrew_days_in_year(y)

def hebrew_days_in_year(y):
  return calendrical.hebrew_days_in_year(y)

def long_heshvan(y):
  return calendrical.long_heshvan(y)

def short_kislev(y):
  return calendrical.short_kislev(y)

def absolute_from_hebrew(*x):
  m, d, y = _get3_(x)
  return calendrical.hebrew_to_rd(y, m, d)

def hebrew_from_absolute(a):
  y, m, d = calendrical.rd_to_hebrew(a)
  return m, d, y

def Nth_Kday(n, k, m, y):
  return calendrical.nth_kday(y, m, n, k)

def nicaean_rule_easter(y):
  return calendrical.nicaean_rule_easter(y)

def easter(y):
  return calendrical.easter(y)

def absolute_from_mayan_long_count(*x):
  return calendrical.mayan_long_count_to_rd(*x)

def mayan_long_count_from_absolute(a):
  return calendrical.rd_to_mayan_long_count(a)

def mayan_haab_from_absolute(a):
  m, md = calendrical.rd_to_mayan_haab(a)
  return md, m

def mayan_haab_difference(*x):
  md1, m1, md2, m2 = _get22_(x)
  return calendrical.mayan_haab_difference(m1, md1, m2, md2)

def mayan_haab_on_or_before(*x):
  md, m, a = _get21_(x)
  return calendrical.mayan_haab_on_or_before(m, md, a)

def mayan_tzolkin_from_absolute(a):
  na, nu = calendrical.rd_to_mayan_tzolkin(a)
  return nu, na

def mayan_tzolkin_difference(*x):
  nu1, na1, nu2, na2 = _get22_(x)
  return calendrical.mayan_tzolkin_difference(na1, nu1, na2, nu2)

def mayan_tzolkin_on_or_before(*x):
  nu, na, a = _get21_(x)
  return calendrical.mayan_tzolkin_on_or_before(na, nu, a)

def mayan_haab_tzolkin_on_or_before(*x):
  d, m, nu, na, a = _get221_(x)
  return calendrical.mayan_haab_tzolkin_on_or_before(m, d, na, nu, a)

def french_leap_year(y):
  return calendrical.french_leap_year(y)

def french_last_day_of_month(m, y):
  return calendrical.french_last_day_of_month(y, m)

def absolute_from_french(*x):
  m, d, y = _get3_(x)
  return calendrical.french_to_rd(y, m, d)

def french_from_absolute(a):
  y, m, d = calendrical.rd_to_french(a)
  return m, d, y

def solar_longitude(d):
  return calendrical.solar_longitude(d)

def zodiac(d):
  return calendrical.zodiac(d)

def old_hindu_solar_last_day_of_month(m, y):
  return calendrical.old_hindu_solar_last_day_of_month(y, m)

def absolute_from_old_hindu_solar(*x):
  m, d, y = _get3_(x)
  return calendrical.old_hindu_solar_to_rd(y, m, d)

def old_hindu_solar_from_absolute(a):
  y, m, d = calendrical.rd_to_old_hindu_solar(a)
  return m, d, y

def lunar_longitude(d):
  return calendrical.lunar_longitude(d)

def lunar_phase(d):
  return calendrical.lunar_phase(d)

def new_moon(d):
  return calendrical.new_moon(d)

def old_hindu_lunar_last_day_of_month(m, y):
  return calendrical.old_hindu_lunar_last_day_of_month(y, m)

def old_hindu_lunar_from_absolute(a):
  y, m, l, d = calendrical.rd_to_old_hindu_lunar(a)
  return m, l, d, y

def old_hindu_lunar_precedes(*x):
  m1, l1, md1, y1, m2, l2, md2, y2 = _get44_(x)
  return calendrical.old_hindu_lunar_precedes(y1, m1, l1, md1, y2, m2, l2, md2)

def absolute_from_old_hindu_lunar(*x):
  m, l, d, y = _get4_(x)
  return calendrical.old_hindu_lunar_to_rd(y, m, l, d)

def world_leap_year(y):
  return calendrical.world_leap_year(y)

def world_last_day_of_month(m, y):
  return calendrical.world_last_day_of_month(y, m)

def absolute_from_world(*x):
  m, d, y = _get3_(x)
  return calendrical.world_to_rd(y, m, d)

def world_from_absolute(a):
  y, m, d = calendrical.rd_to_world(a)
  return m, d, y

def world_day_of_week_from_absolute(a):
  return calendrical.rd_to_world_day_of_week(a)

def coptic_leap_year(y):
  return calendrical.coptic_leap_year(y)

def coptic_last_day_of_month(m, y):
  return calendrical.coptic_last_day_of_month(y, m)

def absolute_from_coptic(*x):
  m, d, y = _get3_(x)
  return calendrical.coptic_to_rd(y, m, d)

def coptic_from_absolute(a):
  y, m, d = calendrical.rd_to_coptic(a)
  return m, d, y

def ethiopian_leap_year(y):
  return calendrical.ethiopian_leap_year(y)

def ethiopian_last_day_of_month(m, y):
  return calendrical.ethiopian_last_day_of_month(y, m)

def absolute_from_ethiopian(*x):
  m, d, y = _get3_(x)
  return calendrical.ethiopian_to_rd(y, m, d)

def ethiopian_from_absolute(a):
  y, m, d = calendrical.rd_to_ethiopian(a)
  return m, d, y

def jalaali_leap_year(y):
  return calendrical.jalali_leap_year(y)

def jalaali_last_day_of_month(m, y):
  return calendrical.jalali_last_day_of_month(y, m)

def absolute_from_jalaali(*x):
  m, d, y = _get3_(x)
  return calendrical.jalali_to_rd(y, m, d)

def jalaali_from_absolute(a):
  y, m, d = calendrical.rd_to_jalali(a)
  return m, d, y

def bahai_leap_year(y):
  return calendrical.bahai_leap_year(y)

def bahai_last_day_of_month(m, y):
  return calendrical.bahai_last_day_of_month(y, m)

def absolute_from_bahai(*x):
  m, d, y = _get3_(x)
  return calendrical.bahai_to_rd(y, m, d)

def bahai_from_absolute(a):
  y, m, d = calendrical.rd_to_bahai(a)
  return m, d, y

def bahai_vahid_from_year(*x):
  return calendrical.bahai_year_to_vahid(*x)

def bahai_year_from_vahid(*x):
  return calendrical.bahai_vahid_to_year(*x)

def absolute_from_ordinal_calendar(*x):
  d, y = _get2_(x)
  return calendrical.ordinal_to_rd(y, d)

def ordinal_calendar_from_absolute(a):
  y, d = calendrical.rd_to_ordinal(a)
  return d, y

def julian_day_number_from_absolute(a):
  return calendrical.rd_to_jd(a)

def absolute_from_julian_day_number(j):
  return calendrical.jd_to_rd(j)

def jdn_from_absolute(a):
  return calendrical.rd_to_jd(a)

def absolute_from_jdn(j):
  return calendrical.jd_to_rd(j)

def julian_day_number_from_mjd(m):
  return calendrical.mjd_to_jd(m)

def mjd_from_julian_day_number(j):
  return calendrical.jd_to_mjd(j)

def jdn_from_mjd(m):
  return calendrical.mjd_to_jd(m)

def mjd_from_jdn(j):
  return calendrical.jd_to_mjd(j)

def lilian_day_number_from_absolute(a):
  return calendrical.rd_to_ld(a)

def absolute_from_lilian_day_number(l):
  return calendrical.ld_to_rd(l)

def ldn_from_absolute(a):
  return calendrical.rd_to_ld(a)

def absolute_from_ldn(l):
  return calendrical.ld_to_rd(l)

def day_of_week_from_absolute(a):
  return calendrical.rd_to_day_of_week(a)

def absolute_from_kyureki(*x):
  m, l, d, y = _get4_(x)
  return calendrical.kyureki_to_rd(y, m, l, d)

def kyureki_from_absolute(a):
  y, m, l, d = calendrical.rd_to_kyureki(a)
  return m, l, d, y

def kyureki_day_of_week_from_absolute(a):
  return calendrical.rd_to_kyureki_day_of_week(a)

__version__ = "$Revision: 1.12 FAKE $"
day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
month_names = ["*", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
gregorian_month_names = ["*", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
julian_month_names = ["*", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
islamic_month_names = ["*", "Muharram", "Safar", "Rabi` I", "Rabi` II", "Jumada I", "Jumada II", "Rajab", "Sha`ban", "Ramadan", "Shawwal", "Du al-Qa`da", "Du al-Hijja"]
hebrew_month_names = [["*", "Nisan", "Iyyar", "Sivan", "Tammuz", "Av", "Elul", "Tishri", "Heshvan", "Kislev", "Teveth", "Shevat", "Adar"], ["*", "Nisan", "Iyyar", "Sivan", "Tammuz", "Av", "Elul", "Tishri", "Heshvan", "Kislev", "Teveth", "Shevat", "Adar I", "Adar II"]]
mayan_haab_month_names = ["*", "Pop", "Uo", "Zip", "Zotz", "Tzec", "Xul", "Yaxkin", "Mol", "Chen", "Yax", "Zac", "Ceh", "Mac", "Kankin", "Muan", "Pax", "Kayab", "Cumku", "Uayeb"]
mayan_tzolkin_month_names = ["*", "Imix", "Ik", "Akbal", "Kan", "Chicchan", "Cimi", "Manik", "Lamat", "Muluc", "Oc", "Chuen", "Eb", "Ben", "Ix", "Men", "Cib", "Caban", "Etznab", "Cauac", "Ahau"]
french_month_names = ["*", "Vende'miaire", "Brumaire", "Frimaire", "Nivo^se", "Pluvio^se", "Vento^se", "Germinal", "Flore'al", "Prairial", "Messidor", "Thermidor", "Fructidor", "*"]
french_day_names = ["*", "Primidi", "Doudi", "Tridi", "Quartidi", "Quintidi", "Sextidi", "Septidi", "Octidi", "Nonidi", "Decadi"]
french_sansculottides_names = ["*", "Vertu", "Genie", "Labour", "Raison", "Recompense", "Revolution", "*", "*", "*", "*"]
old_hindu_solar_month_names = ["*", "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vris'chika", "Dhanu", "Makara", "Kumbha", "Mina"]
old_hindu_lunar_month_names = ["*", "Chaitra", "Vaisa'akha", "Jyaishtha", "Ashadha", "S'ravana", "Bhadrapada", "As'vina", "Karttika", "Margas'ira", "Pausha", "Magha", "Phalguna"]
world_day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "World", "Leap"]
world_month_names = ["*", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
coptic_month_names = ["*", "Tut", "Babah", "Hatur", "Kiyahk", "Tubah", "Amshir", "Baramhat", "Baramundah", "Bashans", "Ba'unah", "Abib", "Misra", "al-Nasi"]
ethiopian_month_names = ["*", "Maskaram", "Teqemt", "Khedar", "Takhs'as'", "Ter", "Yakatit", "Magabit", "Miyazya", "Genbot", "Sane", "Hamle", "Nahase", "Paguemen"]
jalaali_month_names = ["*", "Farvardin", "Ordibehest", "Xordad", "Tir", "Mordad", "Sahrivar", "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"]
kyureki_day_names = ["Senkachi", "Tomobiki", "Semmake", "Butsumetsu", "Taian", "Shakku"]
kyureki_month_names = ["*", "Mutsuki", "Kisaragi", "Yayoi", "Uzuki", "Satsuki", "Minazuki", "Fuzuki", "Hazuki", "Nagatsuki", "Kannazuki", "Shimotsuki", "Shiwasu"]

jalali_month_names = jalaali_month_names
bahai_day_names = calendrical.bahai_day_names
bahai_month_names = calendrical.bahai_month_names
