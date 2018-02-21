// -*-Mode: C;-*-

#ifndef PMU_OVRSR_H
#define PMU_OVRSR_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_ovrsr.h
  \brief  Provides accesss/interface to the Performance Monitors Overflow
          Flag Status Register.
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_ovrsr.h $

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
  This holds the state of the overflow bits for
       - the Cycle Count Register
       - each of the implemented event counters, \e PMXNx.


  \Layout
   The layout of this register is defined in \e pmu_pmnxs.h. This layout
   is common across a number of registers. The meanings of these bits
   for this register is defined here:

  \verbatim

   |31|30             N | N-1                         |
   +--+-----------------+-----------------------------+
   | C| Reserved RAZ/WI | Event Counter overflow bits |
   +--+-----------------+-----------------------------+

  \endverbatim

   where \e N is the number of counters in the implemented version of the
   Performance Monitor Unit.  On the Znyq, N = 6 counters.  

   \e C = overflow status bit for the PMCCNTR


  \note
   Bits > N will read 0. 


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
/* REGISTER ACCESS: Performance Monitor CNTENSET Register                 */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_ovrsr_read    ();
static void         pmu_ovrsr_write   (unsigned int ovrsr);

static unsigned int pmu_ovrsr_pxs_get (unsigned int ovrsr);
static unsigned int pmu_ovrsr_c_get   (unsigned int ovrsr);

static unsigned int pmu_ovrsr_pxs_set (unsigned int ovrsr,
                                        unsigned int  pxs);
static unsigned int pmu_ovrsr_c_set   (unsigned int ovrsr,
                                       unsigned int    c);

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief   Primitive to read PMOVRSR, the Performance Monitor Overflow
           Flag Status Set Register.
  \return  The value of the Performance Monitor Overflow Flag Status
           Register.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_ovrsr_read ()
{
    unsigned int ovrsr;
    asm volatile (" MRC     p15, 0, %0, c9, c12, 3" : "=r"(ovrsr) ::);
    return ovrsr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief     Primitive to write PMOVRSR, the Performance Monitor
             Overflow Flag Status Register.

  \param[in] ovrsr  The value of the Performance Monitor Overflow Flag
                    Status Register to write.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_ovrsr_write (unsigned int ovrsr)
{
    asm volatile (" MCR     p15, 0, %0, c9, c12, 3" : : "r"(ovrsr) :);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a bit mask corresponding to the event counters that 
          have overflowed.
  \return A bit mask corresponding to the event counters that have
          overflowed.

  \param[in] ovrsr The Performance Monitor Overflow Flag Status Register
                   value.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_ovrsr_pxs_get (unsigned int ovrsr)
{
    unsigned int pxs = pmu_pmnxs_pxs_get (ovrsr);
    return pxs;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a flag corresponding to whether the Cycle Counter has
          overflowed
  \return A bit mask corresponding to whether the Cycle Count has 
          overflowed

  \param[in] ovrsr The Performance Monitor Overflow Flag Status Register
                      value.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_ovrsr_c_get (unsigned int ovrsr)
{
    unsigned int c = pmu_pmnxs_c_get (ovrsr);
    return c;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the overflow status of the event counters
  \return The new value of the Performance Monitors Overflow Flag Status
          Register.

  \param[in] ovrsr  The Performance Monitors Overflow Flag Status
                    Register value.
  \param[in] pxs    The overflow status of the event counters.

  \note
   The set of counters does not include the Cycle Counter.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_ovrsr_pxs_set (unsigned int ovrsr,
                                              unsigned  int  pxs)
{
    ovrsr = pmu_pmnxs_pxs_set (ovrsr, pxs);
    return ovrsr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the overflow status of the Cyclic counter.
  \return The new value of the Performance Monitors Overflow Flag Status
          Register.

  \param[in] ovrsr The Performance Monitors Overflow Flag Status Register
                   value.
  \param[in] c     The overflow status of the Cycle Counter

                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_ovrsr_c_set (unsigned int ovrsr,
                                            unsigned int     c)
{
    ovrsr = pmu_pmnxs_c_set (ovrsr, c);
    return ovrsr;
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif

#endif
