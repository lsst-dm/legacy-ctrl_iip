// -*-Mode: C;-*-

#ifndef PMU_CCNTR_H
#define PMU_CCNTR_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_ccntr.h
  \brief  Provides accesss/interface to the Performance Monitors Common 
          Event ID Register 1
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_ccntr.h $

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
   The PMCCNTR holds the value of the processor Cycle Counter, CCNT, that
   counts processor clock cycles. The PMCR.D bit (in the Performance
   Monitors Control Register, configures whether PMCCNTR increments once
   every clock cycle, or once every 64 clock cycles.

  \Layout

  \verbatim

   |31 |   |   |   |   |   |   |   0|
   +--------------------------------+
   |              CCNT              |
   +--------------------------------+

  \endvertabim

                                                                          */
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *\
 * 
 * HISTORY
 * -------
 *
 * DATE     WHO WHAT
 * -------- --- ---------------------------------------------------------
 * 05.05.13 jjr Created
 *
\* ---------------------------------------------------------------------- */


#ifdef __cplusplus
extern "C"
{
#endif


/* ---------------------------------------------------------------------- */
/* REGISTER ACCESS: Performance Monitor CCNTR Register                    */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_ccntr_read  ();
static void         pmu_ccntr_write (unsigned int ccntr);

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Primitive to read PMCCNTR, the Performance Monitor Cycle Count
          Register.
  \return The value of the Performance Monitor Cycle Count Register.

   The PMCCNTR holds the value of the processor Cycle Counter, that counts
   processor cycles.  This is a 32-bit unsigned integer.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_ccntr_read ()
{
    unsigned int reg;
    asm volatile (" MRC     p15, 0, %0, c9, c13, 0" : "=r"(reg) ::);
    return reg;
}
/* ---------------------------------------------------------------------- */


/* ---------------------------------------------------------------------- *//*!

  \brief  Primitive to write PMCCNTR, the Performance Monitor Cycle Count
          Register.

  param[in] ccnt  The count value to write

  While reading the Cycle Count Register is by far the more common
  activity, one possible usage of pre-setting the count is to generate
  an overflow, and hence, an interrupt after N cycles.  To be fair,
  this seems useful only if the interrupt is enabled to the external
  event bus, so that it can be monitored remotely.  However, if pressed,
  one could manufacture a reason to do this only on the processor side
  for some debugging purpose. (Admittedly a stretch...)
                                                                         */
/* ---------------------------------------------------------------------- */
static inline void pmu_ccntr_write (unsigned int ccnt)
{
    asm volatile (" MCR     p15, 0, %0, c9, c13, 0" : : "r"(ccnt) :);
}
/* ---------------------------------------------------------------------- */

#ifdef __cplusplus
}
#endif

#endif
