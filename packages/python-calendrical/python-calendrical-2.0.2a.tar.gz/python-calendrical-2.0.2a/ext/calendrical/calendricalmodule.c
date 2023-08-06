/*
  calendricalmodule.c: Copyright (C) 1997-2002,2008,2014,2018 Tadayoshi Funaba All rights reserved
  $Id: calendricalmodule.c,v 1.17 2018/07/05 10:15:05 tadf Exp $
*/

#include <Python.h>
#include "calendrical.h"
#include "calendrical2.h"
#include "qref.h"

#define CHECK_RANGE(v, m)			\
{						\
    if ((v) < (m)) {				\
	PyErr_SetString				\
	    (PyExc_ValueError,			\
	     "out of range");			\
	return NULL;				\
    }						\
}

#define CHECK_DOMAIN(v, m)			\
{						\
    if ((v) < (m)) {				\
	PyErr_SetString				\
	    (PyExc_ValueError,			\
	     "out of domain");			\
	return NULL;				\
    }						\
}

#define CHECK_DOMAIN2(v, m, n)			\
{						\
    if ((v) < (m) || (v) > (n)) {		\
	PyErr_SetString				\
	    (PyExc_ValueError,			\
	     "out of domain");			\
	return NULL;				\
    }						\
}

static PyObject *
calendrical_gregorian_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = gregorian_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_gregorian_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 12);
    md = gregorian_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_gregorian_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 31);
    a = gregorian_to_rd(y, m, md);
    rd_to_gregorian(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_gregorian(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_gregorian(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_kday_on_or_before(PyObject *self, PyObject *args)
{
    int a, k, b;

    if (!PyArg_ParseTuple(args, "ii", &a, &k))
	return NULL;
    CHECK_DOMAIN2(k, 0, 6);
    b = kday_on_or_before(a, k);
    return Py_BuildValue("i", b);
}

static PyObject *
calendrical_iso_to_rd(PyObject *self, PyObject *args)
{
    int y, w, wd, a, y2, w2, wd2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &w, &wd))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &w, &wd))
	    return NULL;
    }
    CHECK_DOMAIN2(w, 1, 53);
    CHECK_DOMAIN2(wd, 1, 7);
    a = iso_to_rd(y, w, wd);
    rd_to_iso(a, &y2, &w2, &wd2);
    if (w != w2 || wd != wd2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_iso(PyObject *self, PyObject *args)
{
    int a, y, w, wd;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_iso(a, &y, &w, &wd);
    return Py_BuildValue("(iii)", y, w, wd);
}

static PyObject *
calendrical_julian_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = julian_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_julian_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 12);
    md = julian_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_julian_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 31);
    a = julian_to_rd(y, m, md);
    rd_to_julian(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_julian(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_julian(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_islamic_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = islamic_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_islamic_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 12);
    md = islamic_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_islamic_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 30);
    a = islamic_to_rd(y, m, md);
    rd_to_islamic(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_islamic(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_islamic(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_hebrew_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = hebrew_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_hebrew_last_month_of_year(PyObject *self, PyObject *args)
{
    int y, m;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    m = hebrew_last_month_of_year(y);
    return Py_BuildValue("i", m);
}

static PyObject *
calendrical_hebrew_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 13);
    md = hebrew_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_hebrew_calendar_elapsed_days(PyObject *self, PyObject *args)
{
    int y, d;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    d = hebrew_calendar_elapsed_days(y);
    return Py_BuildValue("i", d);
}

static PyObject *
calendrical_hebrew_days_in_year(PyObject *self, PyObject *args)
{
    int y, d;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    d = hebrew_days_in_year(y);
    return Py_BuildValue("i", d);
}

static PyObject *
calendrical_long_heshvan(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = long_heshvan(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_short_kislev(PyObject *self, PyObject *args)
{
    int y, s;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    s = short_kislev(y);
    return Py_BuildValue("i", s);
}

static PyObject *
calendrical_hebrew_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 13);
    CHECK_DOMAIN2(md, 1, 30);
    a = hebrew_to_rd(y, m, md);
    rd_to_hebrew(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_hebrew(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_hebrew(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_nth_kday(PyObject *self, PyObject *args)
{
    int y, m, n, k, b;

    if (!PyArg_ParseTuple(args, "iiii", &y, &m, &n, &k))
	return NULL;
    if (n < -5 || n == 0 || n > 5)
	PyErr_SetString(PyExc_ValueError, "out of range");
    CHECK_DOMAIN2(k, 0, 6);
    CHECK_DOMAIN2(m, 1, 12);
    b = nth_kday(y, m, n, k);
    return Py_BuildValue("i", b);
}

static PyObject *
calendrical_nicaean_rule_easter(PyObject *self, PyObject *args)
{
    int y, a;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    a = nicaean_rule_easter(y);
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_easter(PyObject *self, PyObject *args)
{
    int y, a;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    a = easter(y);
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_mayan_long_count_to_rd(PyObject *self, PyObject *args)
{
    int bt, kt, t, u, k, a, bt2, kt2, t2, u2, k2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iiiii)", &bt, &kt, &t, &u, &k))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iiiii", &bt, &kt, &t, &u, &k))
	    return NULL;
    }
    CHECK_DOMAIN2(kt, 0, 19);
    CHECK_DOMAIN2(t, 0, 19);
    CHECK_DOMAIN2(u, 0, 17);
    CHECK_DOMAIN2(k, 0, 19);
    a = mayan_long_count_to_rd(bt, kt, t, u, k);
    rd_to_mayan_long_count(a, &bt2, &kt2, &t2, &u2, &k2);
    if (bt != bt2 || kt != kt2 || t != t2 || u != u2 || k != k2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_mayan_long_count(PyObject *self, PyObject *args)
{
    int a, bt, kt, t, u, k;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_mayan_long_count(a, &bt, &kt, &t, &u, &k);
    return Py_BuildValue("(iiiii)", bt, kt, t, u, k);
}

static PyObject *
calendrical_mayan_haab_from_rd(PyObject *self, PyObject *args)
{
    int a, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_mayan_haab(a, &m, &md);
    return Py_BuildValue("(ii)", m, md);
}

static PyObject *
calendrical_mayan_haab_difference(PyObject *self, PyObject *args)
{
    int m1, md1, m2, md2, d;

    if (PyTuple_Size(args) == 2) {
	if (!PyArg_ParseTuple(args, "(ii)(ii)", &m1, &md1, &m2, &md2))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iiii", &m1, &md1, &m2, &md2))
	    return NULL;
    }
    CHECK_DOMAIN2(md1, 0, 19);
    CHECK_DOMAIN2(m1, 1, 19);
    CHECK_DOMAIN2(md2, 0, 19);
    CHECK_DOMAIN2(m2, 1, 19);
    d = mayan_haab_difference(m1, md1, m2, md2);
    return Py_BuildValue("i", d);
}

static PyObject *
calendrical_mayan_haab_on_or_before(PyObject *self, PyObject *args)
{
    int m, md, a, d;

    if (PyTuple_Size(args) == 2) {
	if (!PyArg_ParseTuple(args, "(ii)i", &m, &md, &a))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &m, &md, &a))
	    return NULL;
    }
    CHECK_DOMAIN2(md, 0, 19);
    CHECK_DOMAIN2(m, 1, 19);
    d = mayan_haab_on_or_before(m, md, a);
    return Py_BuildValue("i", d);
}

static PyObject *
calendrical_mayan_tzolkin_from_rd(PyObject *self, PyObject *args)
{
    int a, na, nu;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_mayan_tzolkin(a, &na, &nu);
    return Py_BuildValue("(ii)", na, nu);
}

static PyObject *
calendrical_mayan_tzolkin_difference(PyObject *self, PyObject *args)
{
    int na1, nu1, na2, nu2, d;

    if (PyTuple_Size(args) == 2) {
	if (!PyArg_ParseTuple(args, "(ii)(ii)", &na1, &nu1, &na2, &nu2))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iiii", &na1, &nu1, &na2, &nu2))
	    return NULL;
    }
    CHECK_DOMAIN2(nu1, 1, 13);
    CHECK_DOMAIN2(na1, 1, 20);
    CHECK_DOMAIN2(nu2, 1, 13);
    CHECK_DOMAIN2(na2, 1, 20);
    d = mayan_tzolkin_difference(na1, nu1, na2, nu2);
    return Py_BuildValue("i", d);
}

static PyObject *
calendrical_mayan_tzolkin_on_or_before(PyObject *self, PyObject *args)
{
    int na, nu, a, d;

    if (PyTuple_Size(args) == 2) {
	if (!PyArg_ParseTuple(args, "(ii)i", &na, &nu, &a))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &na, &nu, &a))
	    return NULL;
    }
    CHECK_DOMAIN2(nu, 1, 13);
    CHECK_DOMAIN2(na, 1, 20);
    d = mayan_tzolkin_on_or_before(na, nu, a);
    return Py_BuildValue("i", d);
}

static PyObject *
calendrical_mayan_haab_tzolkin_on_or_before(PyObject *self, PyObject *args)
{
    int m, md, na, nu, a, d;

    if (PyTuple_Size(args) == 3) {
	if (!PyArg_ParseTuple(args, "(ii)(ii)i", &m, &md, &na, &nu, &a))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iiiii", &m, &md, &na, &nu, &a))
	    return NULL;
    }
    CHECK_DOMAIN2(md, 0, 19);
    CHECK_DOMAIN2(m, 1, 19);
    CHECK_DOMAIN2(nu, 1, 13);
    CHECK_DOMAIN2(na, 1, 20);
    d = mayan_haab_tzolkin_on_or_before(m, md, na, nu, a);
    return Py_BuildValue("i", d);
}

static PyObject *
calendrical_french_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = french_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_french_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 13);
    md = french_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_french_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 13);
    CHECK_DOMAIN2(md, 1, 30);
    a = french_to_rd(y, m, md);
    rd_to_french(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_french(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_french(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_solar_longitude(PyObject *self, PyObject *args)
{
    double d, l;

    if (!PyArg_ParseTuple(args, "d", &d))
	return NULL;
    l = solar_longitude(d);
    return Py_BuildValue("d", l);
}

static PyObject *
calendrical_zodiac(PyObject *self, PyObject *args)
{
    double d, l;

    if (!PyArg_ParseTuple(args, "d", &d))
	return NULL;
    l = zodiac(d);
    return Py_BuildValue("d", l);
}

static PyObject *
calendrical_rd_to_old_hindu_solar(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_old_hindu_solar(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_old_hindu_solar_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 31);
    a = old_hindu_solar_to_rd(y, m, md);
    rd_to_old_hindu_solar(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_lunar_longitude(PyObject *self, PyObject *args)
{
    double d, l;

    if (!PyArg_ParseTuple(args, "d", &d))
	return NULL;
    l = lunar_longitude(d);
    return Py_BuildValue("d", l);
}

static PyObject *
calendrical_lunar_phase(PyObject *self, PyObject *args)
{
    double d, p;

    if (!PyArg_ParseTuple(args, "d", &d))
	return NULL;
    p = lunar_phase(d);
    return Py_BuildValue("d", p);
}

static PyObject *
calendrical_new_moon(PyObject *self, PyObject *args)
{
    double d, n;

    if (!PyArg_ParseTuple(args, "d", &d))
	return NULL;
    n = new_moon(d);
    return Py_BuildValue("d", n);
}

static PyObject *
calendrical_rd_to_old_hindu_lunar(PyObject *self, PyObject *args)
{
    int a, y, m, l, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_old_hindu_lunar(a, &y, &m, &l, &md);
    return Py_BuildValue("(iiii)", y, m, l, md);
}

static PyObject *
calendrical_old_hindu_lunar_precedes(PyObject *self, PyObject *args)
{
    int y1, m1, l1, md1, y2, m2, l2, md2, d;

    if (PyTuple_Size(args) == 2) {
	if (!PyArg_ParseTuple
	    (args, "(iiii)(iiii)", &y1, &m1, &l1, &md1, &y2, &m2, &l2, &md2))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple
	    (args, "iiiiiiii", &y1, &m1, &l1, &md1, &y2, &m2, &l2, &md2))
	    return NULL;
    }
    CHECK_DOMAIN2(m1, 1, 12);
    CHECK_DOMAIN2(md1, 1, 30);
    CHECK_DOMAIN2(m2, 1, 12);
    CHECK_DOMAIN2(md2, 1, 30);
    d = old_hindu_lunar_precedes(y1, m1, l1, md1, y2, m2, l2, md2);
    return Py_BuildValue("i", d);
}

static PyObject *
calendrical_old_hindu_lunar_to_rd(PyObject *self, PyObject *args)
{
    int y, m, l, md, a, y2, m2, l2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iiii)", &y, &m, &l, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iiii", &y, &m, &l, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 30);
    a = old_hindu_lunar_to_rd(y, m, l, md);
    rd_to_old_hindu_lunar(a, &y2, &m2, &l2, &md2);
    if (m != m2 || l != l2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_world_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = world_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_world_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 12);
    md = world_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_world_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 31);
    a = world_to_rd(y, m, md);
    rd_to_world(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_world(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_world(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_rd_to_world_day_of_week(PyObject *self, PyObject *args)
{
    int a, w;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    w = rd_to_world_day_of_week(a);
    return Py_BuildValue("i", w);
}

static PyObject *
calendrical_coptic_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = coptic_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_coptic_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 13);
    md = coptic_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_coptic_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 13);
    CHECK_DOMAIN2(md, 1, 30);
    a = coptic_to_rd(y, m, md);
    rd_to_coptic(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_coptic(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_coptic(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_ethiopian_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = ethiopian_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_ethiopian_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 13);
    md = ethiopian_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_ethiopian_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 13);
    CHECK_DOMAIN2(md, 1, 30);
    a = ethiopian_to_rd(y, m, md);
    rd_to_ethiopian(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_ethiopian(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_ethiopian(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_jalali_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = jalali_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_jalali_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 12);
    md = jalali_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_jalali_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 31);
    a = jalali_to_rd(y, m, md);
    rd_to_jalali(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_jalali(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_jalali(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_bahai_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = bahai_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_bahai_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 20);
    md = bahai_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_bahai_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 20);
    CHECK_DOMAIN2(md, 1, 19);
    a = bahai_to_rd(y, m, md);
    rd_to_bahai(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_bahai(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_bahai(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_bahai_year_to_vahid(PyObject *self, PyObject *args)
{
    int y, k, v, y2;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    bahai_year_to_vahid(y, &k, &v, &y2);
    return Py_BuildValue("(iii)", k, v, y2);
}

static PyObject *
calendrical_bahai_vahid_to_year(PyObject *self, PyObject *args)
{
    int k, v, y, y2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &k, &v, &y))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &k, &v, &y))
	    return NULL;
    }
    CHECK_DOMAIN2(v, 1, 19);
    CHECK_DOMAIN2(y, 1, 19);
    y2 = bahai_vahid_to_year(k, v, y);
    return Py_BuildValue("i", y2);
}

static PyObject *
calendrical_indian_national_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = indian_national_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_indian_national_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 12);
    md = indian_national_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_indian_national_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 31);
    a = indian_national_to_rd(y, m, md);
    rd_to_indian_national(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_indian_national(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_indian_national(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_bengali_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = bengali_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_bengali_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 12);
    md = bengali_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_bengali_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 31);
    a = bengali_to_rd(y, m, md);
    rd_to_bengali(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_bengali(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_bengali(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_nanakshahi_leap_year(PyObject *self, PyObject *args)
{
    int y, l;

    if (!PyArg_ParseTuple(args, "i", &y))
	return NULL;
    l = nanakshahi_leap_year(y);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_nanakshahi_last_day_of_month(PyObject *self, PyObject *args)
{
    int y, m, md;

    if (!PyArg_ParseTuple(args, "ii", &y, &m))
	return NULL;
    CHECK_DOMAIN2(m, 1, 12);
    md = nanakshahi_last_day_of_month(y, m);
    return Py_BuildValue("i", md);
}

static PyObject *
calendrical_nanakshahi_to_rd(PyObject *self, PyObject *args)
{
    int y, m, md, a, y2, m2, md2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iii)", &y, &m, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iii", &y, &m, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 31);
    a = nanakshahi_to_rd(y, m, md);
    rd_to_nanakshahi(a, &y2, &m2, &md2);
    if (m != m2 || md != md2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_nanakshahi(PyObject *self, PyObject *args)
{
    int a, y, m, md;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_nanakshahi(a, &y, &m, &md);
    return Py_BuildValue("(iii)", y, m, md);
}

static PyObject *
calendrical_ordinal_to_rd(PyObject *self, PyObject *args)
{
    int y, yd, a, y2, yd2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(ii)", &y, &yd))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "ii", &y, &yd))
	    return NULL;
    }
    CHECK_DOMAIN2(yd, 1, 366);
    a = ordinal_to_rd(y, yd);
    rd_to_ordinal(a, &y2, &yd2);
    if (yd != yd2 || y != y2) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);

}

static PyObject *
calendrical_rd_to_ordinal(PyObject *self, PyObject *args)
{
    int a, y, yd;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    rd_to_ordinal(a, &y, &yd);
    return Py_BuildValue("(ii)", y, yd);
}

static PyObject *
calendrical_jd_to_rd(PyObject *self, PyObject *args)
{
    int j, a;

    if (!PyArg_ParseTuple(args, "i", &j))
	return NULL;
    a = jd_to_rd(j);
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_jd(PyObject *self, PyObject *args)
{
    int a, j;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    j = rd_to_jd(a);
    return Py_BuildValue("i", j);
}

static PyObject *
calendrical_mjd_to_rd(PyObject *self, PyObject *args)
{
    int m, a;

    if (!PyArg_ParseTuple(args, "i", &m))
	return NULL;
    a = mjd_to_rd(m);
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_mjd(PyObject *self, PyObject *args)
{
    int a, m;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    m = rd_to_mjd(a);
    return Py_BuildValue("i", m);
}

static PyObject *
calendrical_mjd_to_jd(PyObject *self, PyObject *args)
{
    int m, j;

    if (!PyArg_ParseTuple(args, "i", &m))
	return NULL;
    j = mjd_to_jd(m);
    return Py_BuildValue("i", j);
}

static PyObject *
calendrical_jd_to_mjd(PyObject *self, PyObject *args)
{
    int j, m;

    if (!PyArg_ParseTuple(args, "i", &j))
	return NULL;
    m = jd_to_mjd(j);
    return Py_BuildValue("i", m);
}

static PyObject *
calendrical_ld_to_rd(PyObject *self, PyObject *args)
{
    int l, a;

    if (!PyArg_ParseTuple(args, "i", &l))
	return NULL;
    a = ld_to_rd(l);
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_ld(PyObject *self, PyObject *args)
{
    int a, l;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    l = rd_to_ld(a);
    return Py_BuildValue("i", l);
}

static PyObject *
calendrical_rd_to_day_of_week(PyObject *self, PyObject *args)
{
    int a, w;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    w = rd_to_day_of_week(a);
    return Py_BuildValue("i", w);
}

static PyObject *
calendrical_kyureki_to_rd(PyObject *self, PyObject *args)
{
    int y, m, l, md, j, a;
    QDATE q, q2;

    if (PyTuple_Size(args) == 1) {
	if (!PyArg_ParseTuple(args, "(iiii)", &y, &m, &l, &md))
	    return NULL;
    } else {
	if (!PyArg_ParseTuple(args, "iiii", &y, &m, &l, &md))
	    return NULL;
    }
    CHECK_DOMAIN2(m, 1, 12);
    CHECK_DOMAIN2(md, 1, 30);
    q.j = 0;
    q.y = y;
    q.yd = 0;
    q.m = m;
    q.md = md;
    q.wd = 0;
    q.leap = l;
    j = rqref(&q);
    if (j == 0) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    a = jd_to_rd(j);
    qref(j, &q2);
    if (q.y != q2.y || q.m != q2.m || q.md != q2.md || q.leap != q2.leap) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", a);
}

static PyObject *
calendrical_rd_to_kyureki(PyObject *self, PyObject *args)
{
    int a, j;
    QDATE q;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    j = rd_to_jd(a);
    qref(j, &q);
    if (q.j == 0) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("(iiii)", q.y, q.m, q.leap, q.md);
}

static PyObject *
calendrical_rd_to_kyureki_day_of_week(PyObject *self, PyObject *args)
{
    int a, j;
    QDATE q;

    if (!PyArg_ParseTuple(args, "i", &a))
	return NULL;
    j = rd_to_jd(a);
    qref(j, &q);
    if (q.j == 0) {
	PyErr_SetString
	    (PyExc_ValueError,
	     "invalid date");
	return NULL;
    }
    return Py_BuildValue("i", q.wd);
}

static PyMethodDef CalendricalMethods[] = {
    { "gregorian_leap_year", calendrical_gregorian_leap_year, METH_VARARGS },
    { "gregorian_last_day_of_month", calendrical_gregorian_last_day_of_month, METH_VARARGS },
    { "gregorian_to_rd", calendrical_gregorian_to_rd, METH_VARARGS },
    { "rd_to_gregorian", calendrical_rd_to_gregorian, METH_VARARGS },
    { "kday_on_or_before", calendrical_kday_on_or_before, METH_VARARGS },

    { "iso_to_rd", calendrical_iso_to_rd, METH_VARARGS },
    { "rd_to_iso", calendrical_rd_to_iso, METH_VARARGS },
    { "week_date_to_rd", calendrical_iso_to_rd, METH_VARARGS },
    { "rd_to_week_date", calendrical_rd_to_iso, METH_VARARGS },

    { "julian_leap_year", calendrical_julian_leap_year, METH_VARARGS },
    { "julian_last_day_of_month", calendrical_julian_last_day_of_month, METH_VARARGS },
    { "julian_to_rd", calendrical_julian_to_rd, METH_VARARGS },
    { "rd_to_julian", calendrical_rd_to_julian, METH_VARARGS },

    { "islamic_leap_year", calendrical_islamic_leap_year, METH_VARARGS },
    { "islamic_last_day_of_month", calendrical_islamic_last_day_of_month, METH_VARARGS },
    { "islamic_to_rd", calendrical_islamic_to_rd, METH_VARARGS },
    { "rd_to_islamic", calendrical_rd_to_islamic, METH_VARARGS },

    { "hebrew_leap_year", calendrical_hebrew_leap_year, METH_VARARGS },
    { "hebrew_last_month_of_year", calendrical_hebrew_last_month_of_year, METH_VARARGS },
    { "hebrew_last_day_of_month", calendrical_hebrew_last_day_of_month, METH_VARARGS },
    { "hebrew_calendar_elapsed_days", calendrical_hebrew_calendar_elapsed_days, METH_VARARGS },
    { "hebrew_days_in_year", calendrical_hebrew_days_in_year, METH_VARARGS },
    { "long_heshvan", calendrical_long_heshvan, METH_VARARGS },
    { "short_kislev", calendrical_short_kislev, METH_VARARGS },
    { "hebrew_to_rd", calendrical_hebrew_to_rd, METH_VARARGS },
    { "rd_to_hebrew", calendrical_rd_to_hebrew, METH_VARARGS },

    { "nth_kday", calendrical_nth_kday, METH_VARARGS },

    { "nicaean_rule_easter", calendrical_nicaean_rule_easter, METH_VARARGS },
    { "easter", calendrical_easter, METH_VARARGS },

    { "mayan_long_count_to_rd", calendrical_mayan_long_count_to_rd, METH_VARARGS },
    { "rd_to_mayan_long_count", calendrical_rd_to_mayan_long_count, METH_VARARGS },
    { "rd_to_mayan_haab", calendrical_mayan_haab_from_rd, METH_VARARGS },
    { "mayan_haab_difference", calendrical_mayan_haab_difference, METH_VARARGS },
    { "mayan_haab_on_or_before", calendrical_mayan_haab_on_or_before, METH_VARARGS },
    { "rd_to_mayan_tzolkin", calendrical_mayan_tzolkin_from_rd, METH_VARARGS },
    { "mayan_tzolkin_difference", calendrical_mayan_tzolkin_difference, METH_VARARGS },
    { "mayan_tzolkin_on_or_before", calendrical_mayan_tzolkin_on_or_before, METH_VARARGS },
    { "mayan_haab_tzolkin_on_or_before", calendrical_mayan_haab_tzolkin_on_or_before, METH_VARARGS },

    { "french_leap_year", calendrical_french_leap_year, METH_VARARGS },
    { "french_last_day_of_month", calendrical_french_last_day_of_month, METH_VARARGS },
    { "french_to_rd", calendrical_french_to_rd, METH_VARARGS },
    { "rd_to_french", calendrical_rd_to_french, METH_VARARGS },

    { "solar_longitude", calendrical_solar_longitude, METH_VARARGS },
    { "zodiac", calendrical_zodiac, METH_VARARGS },
    { "rd_to_old_hindu_solar", calendrical_rd_to_old_hindu_solar, METH_VARARGS },
    { "old_hindu_solar_to_rd", calendrical_old_hindu_solar_to_rd, METH_VARARGS },
    { "lunar_longitude", calendrical_lunar_longitude, METH_VARARGS },
    { "lunar_phase", calendrical_lunar_phase, METH_VARARGS },
    { "new_moon", calendrical_new_moon, METH_VARARGS },
    { "rd_to_old_hindu_lunar", calendrical_rd_to_old_hindu_lunar, METH_VARARGS },
    { "old_hindu_lunar_precedes", calendrical_old_hindu_lunar_precedes, METH_VARARGS },
    { "old_hindu_lunar_to_rd", calendrical_old_hindu_lunar_to_rd, METH_VARARGS },

    { "world_leap_year", calendrical_world_leap_year, METH_VARARGS },
    { "world_last_day_of_month", calendrical_world_last_day_of_month, METH_VARARGS },
    { "world_to_rd", calendrical_world_to_rd, METH_VARARGS },
    { "rd_to_world", calendrical_rd_to_world, METH_VARARGS },
    { "rd_to_world_day_of_week", calendrical_rd_to_world_day_of_week, METH_VARARGS },

    { "coptic_leap_year", calendrical_coptic_leap_year, METH_VARARGS },
    { "coptic_last_day_of_month", calendrical_coptic_last_day_of_month, METH_VARARGS },
    { "coptic_to_rd", calendrical_coptic_to_rd, METH_VARARGS },
    { "rd_to_coptic", calendrical_rd_to_coptic, METH_VARARGS },

    { "ethiopian_leap_year", calendrical_ethiopian_leap_year, METH_VARARGS },
    { "ethiopian_last_day_of_month", calendrical_ethiopian_last_day_of_month, METH_VARARGS },
    { "ethiopian_to_rd", calendrical_ethiopian_to_rd, METH_VARARGS },
    { "rd_to_ethiopian", calendrical_rd_to_ethiopian, METH_VARARGS },

    { "jalali_leap_year", calendrical_jalali_leap_year, METH_VARARGS },
    { "jalali_last_day_of_month", calendrical_jalali_last_day_of_month, METH_VARARGS },
    { "jalali_to_rd", calendrical_jalali_to_rd, METH_VARARGS },
    { "rd_to_jalali", calendrical_rd_to_jalali, METH_VARARGS },

    { "bahai_leap_year", calendrical_bahai_leap_year, METH_VARARGS },
    { "bahai_last_day_of_month", calendrical_bahai_last_day_of_month, METH_VARARGS },
    { "bahai_to_rd", calendrical_bahai_to_rd, METH_VARARGS },
    { "rd_to_bahai", calendrical_rd_to_bahai, METH_VARARGS },
    { "bahai_year_to_vahid", calendrical_bahai_year_to_vahid, METH_VARARGS },
    { "bahai_vahid_to_year", calendrical_bahai_vahid_to_year, METH_VARARGS },

    { "indian_national_leap_year", calendrical_indian_national_leap_year, METH_VARARGS },
    { "indian_national_last_day_of_month", calendrical_indian_national_last_day_of_month, METH_VARARGS },
    { "indian_national_to_rd", calendrical_indian_national_to_rd, METH_VARARGS },
    { "rd_to_indian_national", calendrical_rd_to_indian_national, METH_VARARGS },

    { "bengali_leap_year", calendrical_bengali_leap_year, METH_VARARGS },
    { "bengali_last_day_of_month", calendrical_bengali_last_day_of_month, METH_VARARGS },
    { "bengali_to_rd", calendrical_bengali_to_rd, METH_VARARGS },
    { "rd_to_bengali", calendrical_rd_to_bengali, METH_VARARGS },

    { "nanakshahi_leap_year", calendrical_nanakshahi_leap_year, METH_VARARGS },
    { "nanakshahi_last_day_of_month", calendrical_nanakshahi_last_day_of_month, METH_VARARGS },
    { "nanakshahi_to_rd", calendrical_nanakshahi_to_rd, METH_VARARGS },
    { "rd_to_nanakshahi", calendrical_rd_to_nanakshahi, METH_VARARGS },

    { "ordinal_to_rd", calendrical_ordinal_to_rd, METH_VARARGS },
    { "rd_to_ordinal", calendrical_rd_to_ordinal, METH_VARARGS },

    { "jd_to_rd", calendrical_jd_to_rd, METH_VARARGS },
    { "rd_to_jd", calendrical_rd_to_jd, METH_VARARGS },

    { "mjd_to_rd", calendrical_mjd_to_rd, METH_VARARGS },
    { "rd_to_mjd", calendrical_rd_to_mjd, METH_VARARGS },

    { "mjd_to_jd", calendrical_mjd_to_jd, METH_VARARGS },
    { "jd_to_mjd", calendrical_jd_to_mjd, METH_VARARGS },

    { "ld_to_rd", calendrical_ld_to_rd, METH_VARARGS },
    { "rd_to_ld", calendrical_rd_to_ld, METH_VARARGS },

    { "rd_to_day_of_week", calendrical_rd_to_day_of_week, METH_VARARGS },

    { "kyureki_to_rd", calendrical_kyureki_to_rd, METH_VARARGS },
    { "rd_to_kyureki", calendrical_rd_to_kyureki, METH_VARARGS },
    { "rd_to_kyureki_day_of_week", calendrical_rd_to_kyureki_day_of_week, METH_VARARGS },
    { NULL, NULL }
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef calendricalmodule = {
  PyModuleDef_HEAD_INIT,
  "calendrical",
  NULL,
  -1,
  CalendricalMethods
};
#endif

PyMODINIT_FUNC
#if PY_MAJOR_VERSION >= 3
PyInit_calendrical(void)
#else
initcalendrical(void)
#endif
{
    PyObject *mod, *dict, *cc_month_names;

#if PY_MAJOR_VERSION >= 3
    mod = PyModule_Create(&calendricalmodule);
    if (mod == NULL)
      return NULL;
#else
    mod = Py_InitModule("calendrical", CalendricalMethods);
    if (mod == NULL)
      return;
#endif

    dict = PyModule_GetDict(mod);

    (void)PyDict_SetItemString
	(dict, "__version__",
	 Py_BuildValue
	 ("s", "$Revision: 1.17 $"));

    (void)PyDict_SetItemString
	(dict, "day_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s]",
	  "Sunday", "Monday", "Tuesday",
	  "Wednesday", "Thursday",
	  "Friday", "Saturday"));
    (void)PyDict_SetItemString
	(dict, "month_names",
	 cc_month_names = Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "January", "February", "March",
	  "April", "May", "June", "July",
	  "August", "September", "October",
	  "November", "December"));

    (void)PyDict_SetItemString
	(dict, "islamic_day_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s]",
	  "al-Aḥad", "al-Ithnayn",
	  "ath-Thalaathaaʼ", "al-Arba‘aa’",
	  "al-Khamīs", "al-Jumu‘ah", "as-Sabt"));
    (void)PyDict_SetItemString
	(dict, "islamic_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Muḥarram", "Ṣafar",
	  "Rabīʿ I", "Rabīʿ II",
	  "Jumādā I", "Jumādā II",
	  "Rajab", "Shaʿbān",
	  "Ramaḍān", "Shawwāl",
	  "Dhū al-Qaʿda", "Dhū al-Ḥijja"));

    (void)PyDict_SetItemString
	(dict, "hebrew_day_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s]",
	  "Yom Rishon", "Yom Sheni", "Yom Shlishi",
	  "Yom Reviʻi", "Yom Chamishi",
	  "Yom Shishi", "Yom Shabbat"));
    (void)PyDict_SetItemString
	(dict, "hebrew_month_names",
	 Py_BuildValue
	 ("[[s,s,s,s,s,s,s,s,s,s,s,s,s,s][s,s,s,s,s,s,s,s,s,s,s,s,s,s]]",
	  "*", "Nisan", "Iyyar",
	  "Sivan", "Tammuz", "Av",
	  "Elul", "Tishri", "Heshvan",
	  "Kislev", "Teveth", "Shevat",
	  "Adar", "*",
	  "*", "Nisan", "Iyyar",
	  "Sivan", "Tammuz", "Av",
	  "Elul", "Tishri", "Heshvan",
	  "Kislev", "Teveth", "Shevat",
	  "Adar I", "Adar II"));

    (void)PyDict_SetItemString
	(dict, "mayan_haab_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Pop", "Wo'",
	  "Sip", "Sotz'", "Sek",
	  "Xul", "Yaxk'in'", "Mol",
	  "Ch'en", "Yax", "Sak'",
	  "Keh", "Mak", "K'ank'in",
	  "Muwan'", "Pax", "K'ayab",
	  "Kumk'u", "Wayeb'"));
    (void)PyDict_SetItemString
	(dict, "mayan_tzolkin_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Imix'", "Ik'",
	  "Ak'b'al", "K'an", "Chikchan",
	  "Kimi", "Manik'", "Lamat",
	  "Muluk", "Ok", "Chuwen",
	  "Eb'", "B'en", "Ix",
	  "Men", "K'ib'", "Kab'an",
	  "Etz'nab'", "Kawak", "Ajaw"));

    (void)PyDict_SetItemString
	(dict, "french_day_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s]",
	  "Primidi", "Doudi",
	  "Tridi", "Quartidi",
	  "Quintidi", "Sextidi",
	  "Septidi", "Octidi",
	  "Nonidi", "Décadi"));
    (void)PyDict_SetItemString
	(dict, "french_sansculottides_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s]",
	  "Vertu", "Génie",
	  "Labour", "Raison",
	  "Récompenses", "Révolution",
	  "*", "*", "*", "*"));
    (void)PyDict_SetItemString
	(dict, "french_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Vendémiaire",
	  "Brumaire", "Frimaire",
	  "Nivôse", "Pluviôse",
	  "Ventôse", "Germinal",
	  "Floréal", "Prairial",
	  "Messidor", "Thermidor",
	  "Fructidor", "(Sansculottides)"));

    (void)PyDict_SetItemString
	(dict, "old_hindu_solar_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Meṣa", "Vṛṣabha",
	  "Mithuna", "Karkaṭa", "Siṃha",
	  "Kanyā", "Tulā", "Vṛścik‌‌‌a",
	  "Dhanu", "Makara", "Kumbha",
	  "Mīna"));
    (void)PyDict_SetItemString
	(dict, "old_hindu_lunar_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Chaitra", "Vaiśākha",
	  "Jyaiṣṭha", "Āṣāḍha",
	  "Śrāvaṇa", "Bhādrapada",
	  "Āśvina", "Kārtika",
	  "Mārgaśīrṣa", "Pauṣa",
	  "Māgha", "Phālguna"));

    (void)PyDict_SetItemString
	(dict, "world_day_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s]",
	  "Sunday", "Monday", "Tuesday",
	  "Wednesday", "Thursday",
	  "Friday", "Saturday",
	  "World", "Leap"));

    (void)PyDict_SetItemString
	(dict, "coptic_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Thout", "Paopi",
	  "Hathor", "Koiak", "Tobi",
	  "Meshir", "Paremhat","Parmouti",
	  "Pashons", "Paoni", "Epip",
	  "Mesori", "Pi Kogi Enavot"));

    (void)PyDict_SetItemString
	(dict, "ethiopian_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Mäskäräm", "Ṭəqəmt",
	  "Ḫədar", "Taḫśaś'", "Ṭərr",
	  "Yäkatit", "Mägabit",
	  "Miyazya", "Gənbot", "Säne",
	  "Ḥamle", "Nähase",
	  "Ṗagʷəmen"));

    (void)PyDict_SetItemString
	(dict, "jalali_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Farvardin",
	  "Ordibehesht ", "Khordad",
	  "Tir", "Mordad", "Shahrivar",
	  "Mehr", "Aban", "Azar",
	  "Dey", "Bahman", "Esfand"));

    (void)PyDict_SetItemString
	(dict, "bahai_day_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s]",
	  "Jamál", "Kamál", "Fiḍál",
	  "‘Idál", "Istijlál",
	  "Istiqlál", "Jalál"));
    (void)PyDict_SetItemString
	(dict, "bahai_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Bahá", "Jalál",
	  "Jamál", "‘Aẓamat", "Núr",
	  "Raḥmat", "Kalimát", "Kamál",
	  "Asmá’", "‘Izzat", "Mashíyyat",
	  "‘Ilm", "Qudrat", "Qawl",
	  "Masá’il", "Sharaf", "Sulṭán",
	  "Mulk", "Ayyám-i-Há", "‘Alá’"));
    (void)PyDict_SetItemString
	(dict, "bahai_vahid_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Alif", "Bá’",
	  "Ab", "Dál", "Báb",
	  "Váv",  "Abad", "Jád",
	  "Bahá'", "Ḥubb", "Bahháj",
	  "Javáb", "Aḥad", "Vahháb",
	  "Vidád", "Badí‘", "Bahí",
	  "Abhá", "Váḥid"));

    (void)PyDict_SetItemString
	(dict, "indian_national_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Chaitra", "Vaishākha",
	  "Jyaishtha", "Āshādha",
	  "Shrāvana", "Bhādrapada",
	  "Āshwin", "Kārtika",
	  "Agrahayana", "Pausha",
	  "Māgha", "Phālguna"));

    (void)PyDict_SetItemString
	(dict, "bengali_day_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s]",
	  "Rôbibar", "Sombar",
	  "Mônggôlbar", "Budhbar",
	  "Brihôspôtibar", "Shukrôbar",
	  "Shônibar"));
    (void)PyDict_SetItemString
	(dict, "bengali_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Bôishakh", "Jyôishţhô",
	  "Ashaŗh", "Shrabôn",
	  "Bhadrô", "Ashbin",
	  "Kartik", "Ogrôhayôn",
	  "Poush", "Magh",
	  "Falgun", "Chôitrô"));

    (void)PyDict_SetItemString
	(dict, "nanakshahi_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Chet",
	  "Vaisakh", "Jeth",
	  "Harh", "Sawan",
	  "Bhadon", "Assu",
	  "Katak", "Maghar",
	  "Poh", "Magh",
	  "Phagun"));

    (void)PyDict_SetItemString
	(dict, "kyureki_day_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s]",
	  "Senkachi", "Tomobiki",
	  "Semmake", "Butsumetsu",
	  "Taian", "Shakku"));
    (void)PyDict_SetItemString
	(dict, "kyureki_month_names",
	 Py_BuildValue
	 ("[s,s,s,s,s,s,s,s,s,s,s,s,s]",
	  "*", "Mutsuki", "Kisaragi",
	  "Yayoi", "Uzuki", "Satsuki",
	  "Minazuki", "Fuzuki",
	  "Hazuki", "Nagatsuki",
	  "Kannazuki", "Shimotsuki",
	  "Shiwasu"));

    (void)PyDict_SetItemString
	(dict, "gregorian_month_names", cc_month_names);
    (void)PyDict_SetItemString
	(dict, "julian_month_names", cc_month_names);
    (void)PyDict_SetItemString
	(dict, "world_month_names", cc_month_names);

#if PY_MAJOR_VERSION >= 3
    return mod;
#else
    return;
#endif
}
