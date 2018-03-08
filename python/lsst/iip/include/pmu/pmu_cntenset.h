// -*-Mode: C;-*-

#ifndef PMU_CNTENSET_H
#define PMU_CNTENSET_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_cntenset.h
  \brief  Provides accesss/interface to the Performance Monitors Count
          Enable Set Register.
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_cntenset.h $

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
   The PMCNTENSET register enables the Cycle Count Register, PMCCNTR, and 
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
   | C| Reserved RAZ/WI | Event Counter Enable Bits  |
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
/* REGISTER ACCESS: Performance Monitor CNTENSET Register                 */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_cntenset_read  ();
static void         pmu_cntenset_write (unsigned int  cntenset);

static unsigned int pmu_cntenset_pxs_get  (unsigned int cntenset);
static unsigned int pmu_cntenset_c_get    (unsigned int cntenset);

static unsigned int pmu_cntenset_pxs_set  (unsigned int cntenset,
                                           unsigned int      pxs);
static unsigned int pmu_cntenset_c_set    (unsigned int cntenset,
                                           unsigned int        c);

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief   Primitive to read PMCNTENSET, the Performance Monitor Count
           Enable Set Register.
  \return  The value of the Performance Monitor Count Enable Set
           Register.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cntenset_read ()
{
    unsigned int cntenset;
    asm volatile (" MRC     p15, 0, %0, c9, c12, 1" : "=r"(cntenset) ::);
    return cntenset;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief     Primitive to write PMCNENTSET, the Performance Monitor
             Count Enable Set Register.

  \param[in] cntenset  The value of the Performance Monitor Count Enable
                       Set Register to write.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_cntenset_write (unsigned int cntenset)
{
    asm volatile (" MCR     p15, 0, %0, c9, c12, 1" : : "r"(cntenset) :);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a bit mask corresponding to the enabled event counters.
  \return A bit mask corresponding to the enabled event counters.

  \param[in] cntenset The Performance Monitor Count Enable Set Register
                      value.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cntenset_pxs_get  (unsigned int cntenset)
{
    unsigned int pxs = pmu_pmnxs_pxs_get (cntenset);
    return pxs;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a flag corresponding to whether the Cycle Counter is
          enabled.
  \return A bit mask corresponding to the enabled event counters.

  \param[in] cntenset The Performance Monitor Count Enable Set Register
                      value.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cntenset_c_get    (unsigned int cntenset)
{
    unsigned int c = pmu_pmnxs_c_get (cntenset);
    return c;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the event counters to be enabled

  \param[in] cntenset  The Performance Monitors Count Enable Set 
                       Register value.
  \param[in] pxs       The bit mask of event counters to enable

  \note
   The set of counters does not include the Cycle Counter.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cntenset_pxs_set (unsigned int cntenset,
                                                 unsigned int      pxs)
{
    cntenset = pmu_pmnxs_pxs_set (cntenset, pxs);
    return cntenset;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the Cycle counter enable bit

  \param[in] cntenset The Performance Monitors Count Enable Set 
                      Register value.
  \param[in] c        The enable bit value for the Cycle Counter
                         - 0 No action write is ignored
                         - 1 Enable the cycle counter
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cntenset_c_set (unsigned int cntenset,
                                               unsigned int        c)
{
    cntenset = pmu_pmnxs_c_set (cntenset, c);
    return cntenset;
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif

#endif
