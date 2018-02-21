// -*-Mode: C;-*-

#ifndef PMU_INTENCLR_H
#define PMU_INTENCLR_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_intenclr.h
  \brief  Provides accesss/interface to the Performance Monitors Count
          Enable Clear Register.
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_intenclr.h $

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
   The PMINTENCLR register disables the Cycle Count Register, PMCINTR, and 
   any implemented event counters, \i.e. PMNx. Reading this register shows
   which  counters are enabled.
       - 0 = counter disabled 
       - 1 = counter enabled


  \Layout
   The layout of this register is defined in \e pmu_pmnxs.h. This layout
   is common across a number of registers. The meanings of these bits
   for this register is defined here:

  \verbatim

   |31|30             N | N-1                          |
   +--+-----------------+------------------------------+
   | C| Reserved RAZ/WI | Event Interrupt Disable Bits |
   +--+-----------------+------------------------------+

  \endverbatim

   where \e N is the number of counters in the implemented version of the
   Performance Monitor Unit.  On the Znyq, N = 6 counters.  

   \e C = enable/disable bit for the PMCINTR


  \note
   Bits > N will read 0. 

   The result of reading this register and the PMINTENSET register is the
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
/* REGISTER ACCESS: Performance Monitor INTENCLR Register                 */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_intenclr_read    ();
static void         pmu_intenclr_write   (unsigned int  intenclr);

static unsigned int pmu_intenclr_pxs_get (unsigned int intenclr);
static unsigned int pmu_intenclr_c_get   (unsigned int intenclr);

static unsigned int pmu_intenclr_pxs_set (unsigned int intenclr,
                                          unsigned int      pxs);
static unsigned int  pmu_intenclr_c_set  (unsigned int intenclr,
                                          unsigned int        c);

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief   Primitive to read PMINTENCLR, the Performance Monitor Interrupt
           Enable Clear Register.
  \return  The value of the Performance Monitor Interrupt Enable Clear
           Register.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_intenclr_read ()
{
    unsigned int intenclr;
    asm volatile (" MRC     p15, 0, %0, c9, c14, 2" : "=r"(intenclr) ::);
    return intenclr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief     Primitive to write PMCNENTCLR, the Performance Monitor
             Interrupt Enable Clear Register.

  \param[in] intenclr  The value of the Performance Monitor Interrupt
                       Enable Clear Register to write.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_intenclr_write (unsigned int intenclr)
{
    asm volatile (" MCR     p15, 0, %0, c9, c14, 2" : : "r"(intenclr) :);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a bit mask corresponding to the event counters with
          interrupts enabled.
  \return A bit mask corresponding to the the event counters with
          interrupts enabled.

  \param[in] intenclr The Performance Monitor Interrupt Enable Clear
                      Register value
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_intenclr_pxs_get (unsigned int intenclr)
{
    unsigned int pxs = pmu_pmnxs_pxs_get (intenclr);
    return pxs;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a flag corresponding to whether the Cycle Counter is
          enabled to deliver interrupts
  \return A bit mask corresponding to the event counters with interrupts
          enabled.

  \param[in] intenclr The Performance Monitor Interpt Enable Clear
                      Register value.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_intenclr_c_get (unsigned int intenclr)
{
    unsigned int c = pmu_pmnxs_c_get (intenclr);
    return c;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the event counters to have interrupt 
          delivery disabled.
  \return The new value of the Performance Monitors Interrupt Enable 
          Clear Register.

  \param[in] intenclr  The Performance Monitors Interrupt Enable Clear 
                       Register value.
  \param[in] pxs       The bit mask of event counters to disable 
                       interrupts.

  \note
   The set of counters does not include the Cycle Counter.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_intenclr_pxs_set (unsigned int intenclr,
                                                 unsigned int      pxs)
{
    intenclr = pmu_pmnxs_pxs_set (intenclr, pxs);
    return intenclr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the Cycle Counter disable bit
  \return The new value of the Performance Monitors Interrupt Enable 
          Clear Register.


  \param[in] intenclr The Performance Monitors Count Enable Clear 
                      Register value.
  \param[in] c        The disable bit value for the Cycle Counter
                         - 0 No action write is ignored
                         - 1 Disable the cycle counter
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_intenclr_c_set (unsigned int intenclr,
                                               unsigned int        c)
{
    intenclr = pmu_pmnxs_c_set (intenclr, c);
    return intenclr;
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif

#endif
