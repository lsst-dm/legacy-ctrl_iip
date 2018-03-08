// -*-Mode: C;-*-

#ifndef PMU_INTENSET_H
#define PMU_INTENSET_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_intenset.h
  \brief  Provides accesss/interface to the Performance Monitors Interrupt
          Enable Set Register.
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_intenset.h $

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
   The PMINTENSET register enables the Cycle Count Register, PMCINTR, and 
   any implemented event counters, \i.e. PMNx. Reading this register shows
   which  counters are enabled.
       - 0 = counter disabled 
       - 1 = counter enabled


  \Layout
   The layout of this register is defined in \e pmu_pmnxs.h. This layout
   is common across a number of registers. The meanings of these bits
   for this register is defined here:

  \verbatim

   |31|30             N | N-1                         |
   +--+-----------------+-----------------------------+
   | C| Reserved RAZ/WI | Event Interrupt Enable Bits |
   +--+-----------------+-----------------------------+

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
/* REGISTER ACCESS: Performance Monitor INTENSET Register                 */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_intenset_read    ();
static void         pmu_intenset_write   (unsigned int  intenset);

static unsigned int pmu_intenset_pxs_get (unsigned int intenset);
static unsigned int pmu_intenset_c_get   (unsigned int intenset);

static unsigned int pmu_intenset_pxs_set (unsigned int intenset,
                                          unsigned int      pxs);
static unsigned int pmu_intenset_c_set   (unsigned int intenset,
                                          unsigned int        c);

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief   Primitive to read PMINTENSET, the Performance Monitor Interrupt
           Enable Set Register.
  \return  The value of the Performance Monitor Interrupt Enable Set
           Register.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_intenset_read ()
{
    unsigned int intenset;
    asm volatile (" MRC     p15, 0, %0, c9, c14, 1" : "=r"(intenset) ::);
    return intenset;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief     Primitive to write PMCNENTSET, the Performance Monitor
             Interrupt Enable Set Register.

  \param[in] intenset  The value of the Performance Monitor Interrupt
                       Enable Set Register to write.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_intenset_write (unsigned int intenset)
{
    asm volatile (" MCR     p15, 0, %0, c9, c14, 1" : : "r"(intenset) :);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a bit mask corresponding to the enabled event counters.
  \return A bit mask corresponding to the enabled event counters.

  \param[in] intenset The Performance Monitor Interrupt Enable Set
                      Register value.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_intenset_pxs_get  (unsigned int intenset)
{
    unsigned int pxs = pmu_pmnxs_pxs_get (intenset);
    return pxs;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a flag corresponding to whether the Cycle Counter is
          enabled.
  \return A bit mask corresponding to the enabled event counters.

  \param[in] intenset The Performance Monitor Interrupt Enable Set
                      Register value.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_intenset_c_get (unsigned int intenset)
{
    unsigned int c = pmu_pmnxs_c_get (intenset);
    return c;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the event counters to be disabled
  \return The new value of the Performance Monitors Interrupt Enable 
          Set Register.

  \param[in] intenset  The Performance Monitors Interrupt Enable Set 
                       Register value.
  \param[in] pxs       The bit mask of event counters to enable

  \note
   The set of counters does not include the Cycle Counter.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_intenset_pxs_set  (unsigned int intenset,
                                                  unsigned int      pxs)
{
    intenset = pmu_pmnxs_pxs_set (intenset, pxs);
    return intenset;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the Cyclic counter disable bit
  \return The new value of the Performance Monitors Interrupt Enable 
          Set Register.

  \param[in] intenset The Performance Monitors Interrupt Enable Set 
                      Register value.
  \param[in] c        The enable bit value for the Cycle Counter
                         - 0 No action write is ignored
                         - 1 Disable the cycle counter
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_intenset_c_set (unsigned int intenset,
                                               unsigned int        c)
{
    intenset = pmu_pmnxs_c_set (intenset, c);
    return intenset;
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif

#endif
