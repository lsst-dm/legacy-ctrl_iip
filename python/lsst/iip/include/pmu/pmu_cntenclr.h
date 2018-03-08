// -*-Mode: C;-*-

#ifndef PMU_CNTENCLR_H
#define PMU_CNTENCLR_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_cntenclr.h
  \brief  Provides accesss/interface to the Performance Monitors Count
          Enable Clear Register.
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_cntenclr.h $

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
   The PMCNTENCLR register disables the Cycle Count Register, PMCCNTR, and 
   any implemented event counters, \i.e. PMNx. Reading this register shows
   which  counters are enabled.
       - 0 = counter disabled 
       - 1 = counter enabled


  \Layout
   The layout of this register is defined in \e pmu_pmnxs.h. This layout
   is common across a number of registers. The meanings of these bits
   for this register is defined here:

  \verbatim

   |31|30             N | N-1                        |
   +--+-----------------+----------------------------+
   | C| Reserved RAZ/WI | Event Counter Disable Bits |
   +--+-----------------+----------------------------+

  \endverbatim

   where \e N is the number of counters in the implemented version of the
   Performance Monitor Unit.  On the Znyq, N = 6 counters.  

   \e C = enable/disable bit for the PMCCNTR


  \note
   Bits > N will read 0. 

   The result of reading this register and the PMCNTENSET register is the
   same. Clearly, they differ on the write function.

  \note
   Since the reserved field is always read as zero and ignored on write,
   no access methods are provided to this field.
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


#include "pmu/pmu_pmnxs.h"

#ifdef __cplusplus
extern "C"
{
#endif


/* ---------------------------------------------------------------------- */
/* REGISTER ACCESS: Performance Monitor CNTENCLR Register                 */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_cntenclr_read  ();
static void         pmu_cntenclr_write (unsigned int  cntenclr);

static unsigned int pmu_cntenclr_pxs_get  (unsigned int cntenclr);
static unsigned int pmu_cntenclr_c_get    (unsigned int cntenclr);

static unsigned int pmu_cntenclr_pxs_set  (unsigned int cntenclr,
                                           unsigned int      pxs);
static unsigned int pmu_cntenclr_c_set   (unsigned int cntenclr,
                                          unsigned int        c);

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief   Primitive to read PMCNTENCLR, the Performance Monitor Control 
           Enable Clear Register.
  \return  The value of the Performance Monitor Control Enable Clear
           Register.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cntenclr_read ()
{
    unsigned int cntenclr;
    asm volatile (" MRC     p15, 0, %0, c9, c12, 2" : "=r"(cntenclr) ::);
    return cntenclr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief     Primitive to write PMCNENTCLR, the Performance Monitor
             Count Enable Clear Register.

  \param[in] cntenclr  The value of the Performance Monitor Count Enable
                       Clear Register to write.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_cntenclr_write (unsigned int cntenclr)
{
    asm volatile (" MCR     p15, 0, %0, c9, c12, 2" : : "r"(cntenclr) :);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a bit mask corresponding to the enabled event counters.
  \return A bit mask corresponding to the enabled event counters.

  \param[in] cntenclr The Performance Monitor Count Enable Clear Register
                      value.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cntenclr_pxs_get (unsigned int cntenclr)
{
    unsigned int pxs = pmu_pmnxs_pxs_get (cntenclr);
    return pxs;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a flag corresponding to whether the Cycle Counter is
          enabled.
  \return A bit mask corresponding to the enabled event counters.

  \param[in] cntenclr The Performance Monitor Count Enable Clear Register
                      value.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cntenclr_c_get (unsigned int cntenclr)
{
    unsigned int c = pmu_pmnxs_c_get (cntenclr);
    return c;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the event counters to be disabled
  \return The new value of the Performance Monitor Count Enable Clear
          Register.


  \param[in] cntenclr  The Performance Monitors Count Enable Clear 
                       Register value.
  \param[in] pxs       The bit mask of event counters to disable.

  \note
   The set of counters does not include the Cycle Counter.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cntenclr_pxs_set (unsigned int cntenclr,
                                                 unsigned int      pxs)
{
    cntenclr = pmu_pmnxs_pxs_set (cntenclr, pxs);
    return cntenclr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the Cycle Counter disable bit
  \return The new value of the Performance Monitor Count Enable Clear
          Register.

  \param[in] cntenclr The Performance Monitors Count Enable Clear 
                      Register value.
  \param[in] c        The disable bit value for the Cycle Counter
                         - 0 No action write is ignored
                         - 1 Disable the cycle counter
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cntenclr_c_set (unsigned int cntenclr,
                                               unsigned int        c)
{
    cntenclr = pmu_pmnxs_c_set (cntenclr, c);
    return cntenclr;
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif

#endif
