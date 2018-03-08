// -*-Mode: C;-*-

#ifndef PMU_XEVCNTR_H
#define PMU_XEVCNTR_H

/* ---------------------------------------------------------------------- *//*!

  \file   pmu_evtcntr.h
  \brief  Provides access/interface to the Performance Monitors Event
          Count Register
           Register
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
      \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_xevcntr.h $

  \par Credits:
        SLAC

  \verbatim
                               Copyright 2013
                                    by
                       The Board of Trustees of the
                    Leland Stanford Junior University.
                           All rights reserved.
  \endverbatim

  \Purpose
   When PMSELR.SEL selects an event counter, the value of this register
   will be read or write the event counts for that event counter. The
   value selected must be less than the implemented number of counters.
   Thus it is not permitted to PMSELR.SEL = 31, to read or write 
   PMCCNTR

   \verbatim

   |31                                  0|
   +-------------------------------------+
   |  Value of the selecect event counter|
   +-------------------------------------+

   \endverbatim

                                                                          */
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *\
 * 
 * HISTORY
 * -------
 *
 * DATE     WHO WHAT
 * -------- --- ---------------------------------------------------------
 * 05.08.13 jjr Created
 *
\* ---------------------------------------------------------------------- */


#include  "pmu/pmu_common.h"

#ifdef __cplusplus
extern "C"
{
#endif


/* ---------------------------------------------------------------------- */
/* REGISTER ACCESS: Performance Monitor Control Register                  */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_xevcntr_read  ();
static void         pmu_xevcntr_write (unsigned int xevcntr);

/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Primitive to read PMXEVCNTR, the Performance Monitor Event
          Count Register.
  \return The value of the Performance Monitor Event Count Register.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevcntr_read ()
{
    unsigned int reg;
    asm volatile (" MRC     p15, 0, %0, c9, c13, 2" : "=r"(reg) : : "memory");
    return reg;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Primitive to write PMXEVCNTR, the Performance Monitor Event
          Count Register.

  \param[in] xevtcntr The value to write

  The more common way to set a counter to 0 would be to reset all the 
  event counters, but this provides a method to reset a particular 
  counter to 0.

 \note An Esoteric Use
  While reading the Cycle Count Register is by far the more common
  activity, one possible usage of pre-setting the count is to generate
  an overflow, and hence, an interrupt after N cycles.  To be fair,
  this seems useful only if the interrupt is enabled to the external
  event bus, so that it can be monitored remotely.  However, if pressed,
  one could manufacture a reason to do this only on the processor side
  for some debugging purpose. (Admittedly a stretch...)

                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_xevcntr_write (unsigned int xevcntr)
{
    asm volatile (" MCR     p15, 0, %0, c9, c13, 2" : : "r"(xevcntr) : "memory");
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif


#endif
