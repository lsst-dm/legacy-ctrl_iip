// -*-Mode: C;-*-

#ifndef PMU_H
#define PMU_H

/* ---------------------------------------------------------------------- *//*!

  \file   pmu.h
  \brief  Provides a 'C' interface to the performance monitor unit
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu.h $

  \par Credits:
       SLAC

  \verbatim
                               Copyright 2013
                                    by
                       The Board of Trustees of the
                    Leland Stanford Junior University.
                           All rights reserved.
  \endverbatim

  \par Overview
   The performance monitor unit provides an application programmer with
   a low overhead, almost non-intrusive method of assessing the
   performance of a piece of code. It does this through the use of 6
   multiplexed counters and one dedicated cycle counter.  The 6 multiplexed
   counter (referred to as pmnxs) can be configured to count around 256
   different events, such as the number memory loads, the number of 
   exceptions, etc.  Not all 256 events are defined and, even within the
   defined events, not all are implemented.

  \par
   The general usage pattern is
       - Disable the counters
       - Configure the multiplexed counters with the events to be monitored
       - Enable the subset of the configured counters.
         Note that this does not necessarily start these counters.  For
         counters to start, the must be enabled both individually and in
         control register's enable bit.
       - Reset (zero) the enabled set
       - Start the counters by enabling the global multiplexed enable bit
         and the cyclic counter enable bit
       - Wait for the monitored routine to complete
       - Stop the counters by disabling the global multiplexed enable bit
       - Read the configured and enabled counters
       - Present the results
  \par
   There are many nuances to this, some of which get a bit esoteric. To that
   end this interface is presented in 3 modes:

       - Easy, an straightforward stop, reset, configure, start stop
         read and print.  They only option one has is the set of 6 
         events to be monitored

       - Intermediate, allowing one more fine-grained control of the 
         above functions, but at the cost of slightly more overhead than
         the advanced interface and more complexity than the easy interface.
         In particular, some pmu registers are read more times and written
         than absolutely necessary, but one has can specify subsets of 
         the counters which cannot be done with the easy interface.

       - Advanced, allowing one access to each pmu raw instruction.  There
         is no bundling of instructions into higher level functionality, but
         this allows the lowest impact on the code being monitored.
  \par
   For most, the \e easy interface will suffice to get one off-the-ground.
   After determining what one is most interested in monitoring using the
   \e easy interface, one can then may tighten things up using the 
   \e intermediate interface. Very few will need resort to the advance
   interface.  

   Each successive interface is implemented using the routines available in
   the lower level interfaces. 

   In addition, there are number of one-time configuration routines. These
   affect things like the cycle counter divisor.  These configuration routines
   can be used with any interface level. 

  \par Naming Conventions
   The hardest part of this was coming up with a consistent naming 
   convention that would allow the user to easily guess the name of the
   needed method without having to dig through this include file or 
   manual.

  \par
   The convention chosen is
       pmu_<target>_<selector>_<verb>

   where 
       <target>    is the general register or set of general registers 
                   that the operations is direct towards
       <selector>  is the subset of the targetted registers that are 
                   being targetted
       <verb>      the operation

  \par Target
   Many of these are very specific.  These are
     - user access bits, \e e.g.  pmu_user_access_disable
     - cycle scaling/divisor bit, \e e.g. pmu_cycle_cnt_div64_set
     - the number of multiplexed counters that are available, \e e.g.
       pmu_ncounters_read

  \par
   An individual programmable multiplex counter is a common target. These
   are routines that begin with pmu_pmnx_. These routines all target one
   specific counter specified by a simple integer (0-5) as the first
   argument. The nuance here is that some operations allow the cyclic 
   counter to be included in this set (as counter 31) while other operations
   most notably select the cyclic counter as a target of a counter read or
   write and the software increment operation does not include this.   

  \par
   The variation of this are the pmu_pmnxs routines which target a set
   of counters. These are the pmu_pmnxs routines and all have as a first
   argument a selector specified by a bit mask or all the counters. These
   latter routines are the pmu_pmall. Here the first argument is not a
   bit mask selector, since it is implicitly the bit-mask corresponding to
   all The same caveat applies here, some operations include the cyclic
   counter, and some do not.

  \par
   When a subset is being specified, the bit mask can be used in either in 
   a \a dense or \a sparse interpretation. In this case the second argument
   (the first is always the bit mask), is either a source or destination
   array with the \a dense or \a sparse specification indicating how the
   elements are associated with the set bits in the bit-mask.

  \par
   In the dense case, the accessed elements re accessed consecutively, 
   i.e. the first set bit target element 0, the second set bit targets
   to element 1, etc.  

  \par
   In the \a spare case, the accessed elements correspond to the bit numbers
   of the set bits. For example, if the bit mask was 0x12, \i.e. bits 1 and
   4, elements 1 and 4 of the array would be targetted.

  \par Verb
   These are fairly self explainatory
        - enable/disable
        - read/write
        - get/set
        - query/configure
        - increment
   Note that most occurs in pairs of \a read and \a write type operations.
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



#include  "pmu/pmu_common.h"
#include  "pmu/pmu_eid.h"

#include  "pmu/pmu_ccntr.h"
#include  "pmu/pmu_ceid0.h"
#include  "pmu/pmu_ceid1.h"
#include  "pmu/pmu_cntenclr.h"
#include  "pmu/pmu_cntenset.h"
#include  "pmu/pmu_cr.h"
#include  "pmu/pmu_intenclr.h"
#include  "pmu/pmu_intenset.h"
#include  "pmu/pmu_ovrsr.h"
#include  "pmu/pmu_selr.h"
#include  "pmu/pmu_swinc.h"
#include  "pmu/pmu_userenr.h"
#include  "pmu/pmu_xevcntr.h"
#include  "pmu/pmu_xevtyper.h"

#include  <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif


/* ---------------------------------------------------------------------- */
/* EASY LEVEL ROUTINES                                                    */
/*                                                                        */
/* PURPOSE:                                                               */
/* --------                                                               */
/* These routines give an easy to use interface to the performance monitor*/
/* unit at the expense of flexbiity.  They work only with a complete set  */
/* of the 6 counters. That is one configures, queries, and reads all the  */
/* counters. In the case of reading, on reads all 6 counters plus the     */
/* cyclic counter and the overflow flags register.                        */
/*                                                                        */
/* While useful in and of themselves, by examining the code, they can also*/
/* be used a template if more fine-grained control is needed.             */
/*                                                                        */
/* EXAMPLE:                                                               */
/* --------                                                               */
/* unsignded int Eids[6] =                                                */
/* {                                                                      */
/*   PMU_CEID0_K_INST_RETIRED,                                            */
/*   PMU_CEID0_K_LD_RETIRED,                                              */
/*   PMU_CEID0_K_ST_RETIRED,                                              */
/*   PMU_CEID0_K_EXC_TAKEN,                                               */
/*   PMU_CEID0_K_BR_MIS_PRED,                                             */
/*   PMU_CEID0-K_CPU_CYCLES                                               */
/* };                                                                     */
/*                                                                        */
/* PmuResults    results;                                                 */
/* unsigned int    cfg[6];                                                */
/* pmu_stop            ();  // Ensure the counters are stopped            */
/* pmu_configure   (Eids);  // Configure the counters to be monitored     */
/* pmu_reset           ();  // Reset     the counters to be monitored     */
/* pmu_start           ();  // Start     the counters to be monitored     */
/* monitored_routine   ();  // Random code to be monitored                */
/* pmu_stop            ();  // Stop      the counters to be monitored     */
/* pmu_read    (&results);  // Read      the counters                     */
/* pmu_query        (cfg);  // Query     the monitored counters;          */
/*                          // Somewhat unnecessary in this case, since   */
/*                          // this set must be CntIds, but allows for    */
/*                          // for some modularity if the setup stage     */
/*                          // is divorced from the print stage           */
/* pmu_title            (); // Print the title line describing the results*/
/* pmu_print (cfg,results); // Print the results                          */
/*                                                                        */
/* ---------------------------------------------------------------------- */
struct _PmuResults
{
    unsigned int overflow;  /* Overflow flags                             */
    unsigned int   cycles;  /* Number instruction cycles                  */
    unsigned int   cnt[6];  /* The read results of the configured counters*/
};
/* ---------------------------------------------------------------------- */
#ifndef         PMURESULTS_TD
#define         PMURESULTS_TD
typedef struct _PmuResults    PmuResults;
#endif
/* ---------------------------------------------------------------------- */

extern        void pmu_configure (const unsigned int set[6]);
extern        void pmu_print     (const unsigned int evt[6],
                                  const PmuResults *results);
extern        void pmu_query     (unsigned int       cfg[6]);
static inline void pmu_read      (PmuResults       *results);
static inline void pmu_reset     ();
static inline void pmu_start     ();
static inline void pmu_stop      ();
extern        void pmu_title     ();
/* ---------------------------------------------------------------------- */





/* ---------------------------------------------------------------------- */
/* INTERMEDIATE LEVEL ROUTINES                                            */
/*                                                                        */
/* PURPOSE:                                                               */
/* --------                                                               */
/* These routines allow the user somewhat greater control andefficiency   */
/* than the \e easy routines at the cost of somewhat greater complexity.  */
/*                                                                        */
/* In some case, for example the methods dealing with interrupts, while   */
/* there are no corresponding \a easy methods, these methods can be used  */
/* in conjunction with the \a easy methods.                               */
/*                                                                        */
/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Disable/Enable user access to the Performance Monitor Unit             */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMUSERENR, specifcally the \e EN field                                 */
/*                                                                        */
/* These routines may only be called at PL1.                              */
/*                                                                        */
/* ---------------------------------------------------------------------- */
extern void         pmu_user_access_disable      ();
extern void         pmu_user_access_enable       ();
extern void         pmu_user_access_set          (unsigned int access);
extern unsigned int pmu_user_access_is_enabled   ();
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Set/Get the Cycle Counter divisor bit. This controls whether the Cycle */
/* Counter count every processor cycle or every 64th processor cycle.     */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMCR, specifcally the \e D field                                       */
/*                                                                        */
/* ---------------------------------------------------------------------- */
extern void         pmu_cycle_div64_set (unsigned int div64);
extern unsigned int pmu_cycle_div64_get ();
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Obtain the number of event counters implemented in the Performance     */
/* Monitor Unit. This is 6 in V7.3 of the Performance Monitor Unit. This  */
/* value is used when creating software that works across multiple        */
/* versions of the Performance Monitor Unit.                              */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMCR, specifically the N field.                                        */
/*                                                                        */
/* ---------------------------------------------------------------------- */
extern unsigned int pmu_ncounters_read ();
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Configures an event identifier with an event counter. The events are   */
/* defined by the \sa PMU_EID_K enumeration. In addition, this also       */
/* specifies whether counting is filtered by the PL0 and PL1 modes.       */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMSELR and PMXEVTYPER                                                  */
/*                                                                        */
/* This requires the event counter to be selected, via the PMSELR         */
/* register and associated with the event type identifier, via PMEVTYPER. */
/* There also methord to configure a list of counters, the                */
/* pmu_pmnxs_configure and pmx_pmnxs_configure methods.                   */
/*                                                                        */
/* ---------------------------------------------------------------------- */
extern void         pmu_pmnx_configure  (unsigned int     pmnx,
                                         unsigned int evttyper);
extern unsigned int pmu_pmnx_query      (unsigned int     pmnx);
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Configures a list of event identifiers with a corresponding list of    */
/* event counters. The events are defined by the \sa PMU_EID_K            */
/* enumeration. The list may be specified by                              */
/*        - An array of 0-6 event identifiers                             */
/*        - 6 separate arguments, one for each event identifier. This     */
/*            does not provided a much flexibility, but is very convenient*/
/*            when just trying things out                                 */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMSELR and PMXEVTYPER                                                  */
/*                                                                        */
/* These are convenience routines. If only one event counter is being     */
/* configured, use pmu_pmnx_configure.                                    */
/*                                                                        */
/* ---------------------------------------------------------------------- */
extern void pmu_pmnxs_dense_configure  (unsigned int             pmnxs,
                                        unsigned int const xevtypers[]);
extern void pmu_pmnxs_sparse_configure (unsigned int             pmnxs,
                                        unsigned int const xevtypers[]);
extern void pmu_pmall_set_configure    (unsigned int const    event[6]);
extern void pmu_pmall_configure        (unsigned int            event0,
                                        unsigned int            event1,
                                        unsigned int            event2,
                                        unsigned int            event3,
                                        unsigned int            event4,
                                        unsigned int            event5);

extern void pmu_pmnxs_dense_query      (unsigned int             pmnxs,
                                        unsigned int        *xevtypvrs);
extern void pmu_pmnxs_sparse_query     (unsigned int             pmnxs,
                                        unsigned int       xevtypvrs[]);
extern void pmu_pmall_set_query        (unsigned int           event[6]);
extern void pmu_pmall_query            (unsigned int          *event0,
                                        unsigned int          *event1,
                                        unsigned int          *event2,
                                        unsigned int          *event3,
                                        unsigned int          *event4,
                                        unsigned int          *event5);

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Reset the event counters, including the Cycle Counter                  */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMCR, specifically the P and C bits.                                   */
/*                                                                        */
/* Either the Cycle Counter and/or all the event counters can be set.     */
/* The fundamental operations do not include resetting an arbitrary set   */
/* set of counters.  This would have to implemented by writing a 0 to     */
/* each of the counters.                                                  */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static inline void pmu_cycle_cnt_reset       ();
static inline void pmu_pmnxs_cnt_reset       ();
static inline void pmu_global_cnt_reset      ();
static inline void pmu_pmnxs_cycle_cnt_reset (unsigned int which);
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Disable/Enable the counting of all counters including the Cycle        */
/* Counter.                                                               */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMCR, specifically the e E bit                                         */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static void         pmu_global_disable    ();
static void         pmu_global_enable     ();
static void         pmu_global_enbdsb     (unsigned int enable);
static unsigned int pmu_global_is_enabled ();
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Disable/Enable interrupt delivery by individual event counters,        */
/* including the Cycle Counter.                                           */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMINTENCLR and PMINTENSET                                              */
/*                                                                        */
/* Since these registers interact with a set of counters, specified as a  */
/* bit mask, these are convenience methods, which just perform the trivial*/
/* transformation of a counter number to the appropriate bit mask. The    */
/* pmu_pmnxs_cnt set of routines are the more fundamental routines.       */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static inline void         pmu_pmnx_int_disable    (unsigned int    pmnx);
static inline void         pmu_pmnx_int_enable     (unsigned int    pmnx);
static inline void         pmu_pmnx_int_enbdsb     (unsigned int    pmnx,
                                                    unsigned int  enbdsb);
static inline unsigned int pmu_pmnx_int_is_enabled (unsigned int    pmnx);
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Disable/Enable interrupt delivery by a set event counters, including   */
/* the Cycle Counter.                                                     */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMINTENCLR and PMINTENSET                                              */
/*                                                                        */
/* This is a direct interface to the Interrupt Clear and Set Registers.   */
/* If one is only dealing with an individual counter, the pmu_pmnx_int    */
/* routines may allow a clearer expression of that intent.                */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static inline void         pmu_pmall_int_disable     ();
static inline void         pmu_pmall_int_enable      ();
static inline void         pmu_pmnxs_int_disable     (unsigned int pmnxs);
static inline void         pmu_pmnxs_int_enable      (unsigned int pmnxs);
static inline void         pmu_pmnxs_int_enbdsb      (unsigned int pmnxs);
static inline unsigned int pmu_pmnxs_int_are_enabled ();
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Disable/Enable counting by individual event counters, including the    */
/* Cycle Counter                                                          */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMCNTEVCLR and PMCNTEVSET                                              */
/*                                                                        */
/* Since these register interact with a set of counters, specified as a   */
/* bit mask, this is a convenience function. The pmy_pmnxs_cnt set of     */
/* routines are the more fundamental routines.                            */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static void         pmu_pmnx_cnt_disable    (unsigned int   pmnx);
static void         pmu_pmnx_cnt_enable     (unsigned int   pmnx);
static void         pmu_pmnx_cnt_enbdsb     (unsigned int   pmnx,
                                             unsigned int enbdsb);
static unsigned int pmu_pmnx_cnt_is_enabled (unsigned int   pmnx);
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Disable/Enable a set of event counters, including the Cycle Counter    */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMCNTEVCLR and PMCNTEVSET                                              */
/*                                                                        */
/* This is a direct interface to the Event Count Clear and Set Registers. */
/* If one is only dealing with an individual counter, the pmu_pmnx_cnt    */
/* routines may allow a clearer expression of that intent.                */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static void         pmu_pmall_cnt_disable     ();
static void         pmu_pmall_cnt_enable      ();
static void         pmu_pmnxs_cnt_disable     (unsigned int  pmnxs);
static void         pmu_pmnxs_cnt_enable      (unsigned int  pmnxs);
static void         pmu_pmnxs_cnt_enbdsb      (unsigned int  pmnxs);
static unsigned int pmu_pmnxs_cnt_are_enabled ();
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Read/Write the Cycle Counter                                           */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMCCNT                                                                 */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cycle_cnt_read  ();
static inline void         pmu_cycle_cnt_write (unsigned int count);
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Read/Write an individual event counter                                 */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMXEVCNTR                                                              */
/*                                                                        */
/* This is a direct interface to the Event Count Register. If one wishes  */
/* to read/write a set of event counters, consider using the convenience  */
/* routines, pmu_pmnxs_cnt methods.                                       */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_pmnx_cnt_read   (unsigned int       pmnx);
static inline void         pmu_pmnx_cnt_write  (unsigned int       pmnx,
                                                unsigned int      count);
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Read/Write lists of event counters                                     */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMXEVCNTR                                                              */
/*                                                                        */
/* This is a direct interface to the Event Count Register. If one wishes  */
/* to read/write an individual event counters, consider using the         */
/* pmu_pmnx_cnt methods.                                                  */
/*                                                                        */
/* There are convenience methods provided to read a list of counters.     */
/* There are variety of ways the list may be specified.  Currently two    */
/* list types are supported.                                              */
/*      - A sparse bit list                                               */
/*        The event counters to be read/written are specified as a bit    */
/*        list with the destination or source counts selected by the      */
/*        corresponding bit number. i.e. if bit 3 is set, the destination */
/*        or source counter is counter[3].                                */
/*      - A dense bit list                                                */
/*        The event counters to be read/written are specfied as a bit     */
/*        list, with the destination or source count selected by whether  */
/*        this is the first, second, etc bit set.                         */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_cnt_sparse_read  (unsigned int         pmnxs,
                                               unsigned int       *counts);
static inline void pmu_pmnxs_cnt_dense_read   (unsigned int         pmnxs,
                                               unsigned int       *counts);
static inline void pmu_pmall_cnt_set_read     (unsigned int     counts[6]);
static inline void pmu_pmall_cnt_read         (unsigned int        *count0,
                                               unsigned int        *count1,
                                               unsigned int        *count2,
                                               unsigned int        *count3,
                                               unsigned int        *count4,
                                               unsigned int        *count5);

static inline void pmu_pmnxs_cnt_sparse_write(unsigned int          pmnxs,
                                              unsigned int const  *counts);
static inline void pmu_pmnxs_cnt_dense_write (unsigned int          pmnxs,
                                              unsigned int const  *counts);
static inline void pmu_pmall_cnt_set_write   (unsigned int const counts[6]);
static inline void pmu_pmall_cnt_write       (unsigned int          count0,
                                              unsigned int          count1,
                                              unsigned int          count2,
                                              unsigned int          count3,
                                              unsigned int          count4,
                                              unsigned int          count5);


/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Read/Write the event overflow status register, i.e. which event        */
/* counters have overflowed. This includes the Cycle Counter              */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMOVSR                                                                 */
/*                                                                        */
/* This is a direct interface to the Overflow Status Register.            */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static inline void         pmu_pmnxs_ovr_reset (unsigned int pmnxs);
static inline void         pmu_pmall_ovr_reset ();
static inline unsigned int pmu_pmnxs_ovr_read  ();
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- */
/*                                                                        */
/* PURPOSE:                                                               */
/* Read/Write the event software increment register                       */
/*                                                                        */
/* EFFECTED REGISTERS:                                                    */
/* PMOVSR                                                                 */
/*                                                                        */
/* This is a direct interface to the Overflow Status Register.            */
/*                                                                        */
/* ---------------------------------------------------------------------- */
static inline void  pmu_pmnx_software_increment  (unsigned int pmnx);
static inline void  pmu_pmnxs_software_increment (unsigned int pmnxs);
/* ---------------------------------------------------------------------- */








/* ---------------------------------------------------------------------- */
/* EVENT and CYCLE COUNTER RESETS                                         */
/* ---------------------------------------------------------------------- *//*!

  \brief  Resets only the cycle counter, but not the event counters

  \note   If both the event counters and the cycle counter are to be 
          reset, use \sa pmu_reset_all () or if programmable, use
          \sa pmu_reset_counters (which)

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_cycle_cnt_reset ()
{
    unsigned int cr = pmu_cr_read  ();
    cr = pmu_cr_cycle_reset_set (cr, 1);
    pmu_cr_write (cr);
    return;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Resets all the event counters, but not the cycle counter

  \note   If both the event counters and the cycle counter are to be 
          reset, use \sa pmu_all_reset () or if programmable, use
          \pmu_counters_reset (which)

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_cnt_reset ()
{
    unsigned int cr = pmu_cr_read    ();
    cr = pmu_cr_pmnxs_reset_set (cr, 1);
    pmu_cr_write (cr);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Resets both the cycle counter and the event counters

  \note   If only one of the event counters or cycle counter are to be 
          reset, use \sa pmu_pmnx_reset () or pmu_cycle_cnt_reset. If 
          programmable which to reset, use pmu_pmnxs_cnt_reset (pmnxs)

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_global_cnt_reset ()
{
    unsigned int cr = pmu_cr_read  ();
    cr |= (PMU_CR_M_P | PMU_CR_M_C);
    pmu_cr_write (cr);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Resets either the cycle counter or the event counters

  \param[in] which Which counters to reset
                      - 0 None
                      - 1 Only the event counters
                      - 2 Only the cycle counter
                      - 3 Both

  \note   If it is known at complilation time which are to be reset
          consider using
               - pmu_pmnx_cnt_reset to reset the event counters
               - pmu_cycle_cnt_reset to reset the cycle counter
               - pmu_all_reset to reset bot the event and cycle counters

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_cycle_cnt_reset (unsigned int which)
{
    if (which)
    {
        unsigned int cr = pmu_cr_read  ();
        cr |=  (((which       & 1) << PMU_CR_V_P))
           |  ((((which >> 1) & 1) << PMU_CR_V_C));
        pmu_cr_write (cr);
    }

    return;
}
/* ---------------------------------------------------------------------- */


    

/* ---------------------------------------------------------------------- */
/* GLOBAL COUNTER DISABLE/ENABLE                                          */
/* ---------------------------------------------------------------------- *//*!

  \brief  Clear the global counter enable bit, thus diabling all counter

  \note
   This disables all the event counters including the cycle counter, PMCCNTR.

  \par
   Also note that if many fields in the Performance Monitor Control Register
   are being set, it is better to first read the register using \sa
   pmu_cr_read, then use the pmu_cr_xxx_set routines to set the fields.

  Level: Intermediate
                                                                         */
/* ---------------------------------------------------------------------- */
static inline void pmu_global_disable ()
{
    unsigned int cr = pmu_cr_read  ();
    cr = pmu_cr_enable_set   (cr, 0);
    pmu_cr_write (cr);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the global counter enable bit, thus enabling all counters

  \note
   This enables all the event counters including the cycle counter, PMCCNTR.

  \par
   Also note that if many fields in the Performance Monitor Control Register
   are being set, it is better to first read the register using \sa
   pmu_cr_read, then use the pmu_cr_xxx_set routines to set the fields.

  Level: Intermediate
                                                                         */
/* ---------------------------------------------------------------------- */
static inline void pmu_global_enable ()
{
    unsigned int cr = pmu_cr_read ();
    cr = pmu_cr_enable_set  (cr, 1);
    pmu_cr_write (cr);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Set the global counter enable bit to the specified value

  \note
   This enables or disables all the event counters including the cycle 
        counter, PMCCNTR.

  \param[in] enable  The value of the global enable
                         -0  Disable all counters
                         -1  Enable all counters

  Level: Intermediate

  \par
   Also note that if many fields in the Performance Monitor Control Register
   are being set, it is better to first read the register using \sa
   pmu_cr_read, then use the pmu_cr_xxx_set routines to set the fields.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_global_enbdsb (unsigned int enable)
{
    unsigned int    cr = pmu_cr_read  ();
    cr = pmu_cr_enable_set (cr, enable);
    pmu_cr_write (cr);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns whether the all event counters are enabled set or disabled.

  \retval == 0 All event counters are disabled
  \retval == 1 All event counters are enabled

  Level: Intermediate

  \par
   Also note that if many fields in the Performance Monitor Control Register
   are being queried, it is better to first read the register using \sa
   pmu_cr_read, then use the pmu_cr_xxx_get routines to examine the fields.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_global_is_enabled  ()
{
    unsigned int  cr = pmu_cr_read  ();
    unsigned int enb = pmu_cr_enable_get (cr);
    return enb;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- */
/* INTERRUPT DELIVER CONTROL, individual counters                         */
/* ---------------------------------------------------------------------- *//*!

  \brief  Disable the interrupt to a specified event counter

  \param[in] pmnx  The event counter to disable.  This is a value from
                   0 - N-1, where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.

  Level: Intermediate

  If a set of interrputs is being disabled, consider using 
  \sa pmu_irq_pmnxs_disable.  
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnx_int_disable (unsigned int pmnx)
{
    pmu_intenclr_write (1 << pmnx);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Enable the interrupt to a specified event counter

  \param[in] pmnx  The event counter to enable.  This is a value from
                   0 - N-1, where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.

  Level: Intermediate

  If a set of counters is being enabled, consider using 
  \sa pmu_irq_pmnxs_enable.  
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnx_int_enable (unsigned int pmnx)
{
    pmu_intenset_write (1 << pmnx);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Set the interrupt enable for the specified event counter to the
          specified value.

  \param[in] pmnx   The interrtup enable to sett.  This is a value from
                    0 - N-1, where N = the number of event counters, 
                    \e e.g. 6 or 31 for the cycle counter.
  \param[in] enable The enable state to set
                       -0 Disable
                       -1 Enable

  Level: Intermediate

  If a set of counters is being set, consider using \sa pmu_pmnxs_in_enbdsb.  
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnx_int_enbdsb (unsigned int   pmnx,
                                        unsigned int enable)
{
    unsigned int pmnxs = 1 << pmnx;
    if    (enable) pmu_intenset_write (pmnxs);
    else           pmu_intenclr_write (pmnxs);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns whether interrupts to the specified counter are enabled
  \retval == 0, not enabled
  \retval != 0, enabled

  \param[in] pmnx  The event counter to query.  This is a value from
                   0 - N-1, where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.

  If a set of interrupts is being queried, consider using 
  \sa pmu_irq_pmnxs_is_enable.  

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_pmnx_int_is_enabled (unsigned int pmnx)
{
    unsigned int enb = pmu_intenset_read ();
    enb &= 1 << pmnx;
    return enb;
}
/* ---------------------------------------------------------------------- */





/* ---------------------------------------------------------------------- */
/* INTERRUPT DELIVER CONTROL, set of counters                             */
/* ---------------------------------------------------------------------- *//*!

  \brief  Disable interrupt delivery by all event counters

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmall_int_disable ()
{
    pmu_intenclr_write (PMU_PMNXS_M_ALL);
    return;
}
/* ---------------------------------------------------------------------- */


/* ---------------------------------------------------------------------- *//*!

  \brief  Enable interrupt delivery by all event counters

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmall_int_enable ()
{
    pmu_intenset_write (PMU_PMNXS_M_ALL);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Disable the interrupts to a specified set of event counters

  \param[in] pmnxs The set of event counters to disable.  This is a 
                   bit mask, where the valid bit are from 0 - N-1, 
                   where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.   Bit values
                   of 0 are ignored, \i.e. only a 1 causes the counter
                   to be disabled.

  Level: Intermediate

  \note
   Specifying bits representing counters that do not exist is okay. They
   will be ignored by the hardware.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_int_disable (unsigned int pmnxs)
{
    pmu_intenclr_write (pmnxs);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Enable the interrupts to a specified set of event counters

  \param[in] pmnxs The set of event counters to enable.  This is a 
                   bit mask, where the valid bit are from 0 - N-1, 
                   where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.  Bit values
                   of 0 are ignored, \i.e. only a 1 causes the counter
                   to be enabled.

  Level: Intermediate

  \note
   Specifying bits representing counters that do not exist is okay. They
   will be ignored by the hardware.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_int_enable (unsigned int pmnxs)
{
    pmu_intenset_write (pmnxs);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief     Enables \e and disables the interrupts to a specified set of
             event counters.

  \param[in] pmnxs The set of event counters to enable.  This is a 
                   bit mask, where the valid bit are from 0 - N-1, 
                   where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.  Bit values
                   of 
                       0 - disables the counter
                       1 - enables  the counter

  Level: Intermediate

  \note
   Specifying bits representing counters that do not exist is okay. They
   will be ignored by the hardware.  

   This routine provides a method to postively set the enable of the
   interrupts to a known state.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_int_enbdsb (unsigned int pmnxs)
{
    pmu_intenset_write ( pmnxs);
    pmu_intenclr_write (~pmnxs);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns the set of enabled interrupt event counters

  \return A bit mask representing the enabled counters.

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_pmnxs_int_are_enabled  ()
{
    unsigned int reg = pmu_intenset_read ();
    return reg;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- */
/* Disable/Enable a specified event counter                               */
/* ---------------------------------------------------------------------- *//*!

  \brief  Disable a specified event counter

  \param[in] pmnx  The event counter to disable.  This is a value from
                   0 - N-1, where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.

  Level: Intermediate

  If a set of counters is being disabled, consider using 
  \sa pmu_pmnxs_disable.  
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnx_cnt_disable (unsigned int pmnx)
{
    pmu_cntenclr_write (1 << pmnx);
    return;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Enable a specified event counter

  \param[in] pmnx  The event counter to enable.  This is a value from
                   0 - N-1, where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.

  Level: Intermediate

  If a set of counters is being disabled, consider using 
  \sa pmu_pmnxs_cnt_enable.  
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnx_cnt_enable (unsigned int pmnx)
{
    pmu_cntenset_write (1 << pmnx);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Set the enable specified event counter to the specified value.

  \param[in] pmnx   The event counter to set.  This is a value from
                    0 - N-1, where N = the number of event counters, 
                    \e e.g. 6 or 31 for the cycle counter.
  \param[in] enable The disable/enable state to set
                       -0 Disable
                       -1 Enable

  Level: Intermediate

  If a set of counters is being set, consider using \sa pmu_pmnxs_cnt_enbdsb.  
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnx_cnt_enbdsb (unsigned int   pmnx,
                                        unsigned int enable)
{
    unsigned int pmnxs = 1 << pmnx;
    if    (enable) pmu_cntenset_write (pmnxs);
    else           pmu_cntenclr_write (pmnxs);
    return;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Returns whether the specified counter is enabled
  \retval == 0, not enabled
  \retval != 0, enabled

  \param[in] pmnx  The event counter to query.  This is a value from
                   0 - N-1, where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.

  If a set of counters is being queried, consider using 
  \sa pmu_pmnxs_is_enable.  

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_pmnx_cnt_is_enabled (unsigned int pmnx)
{
    unsigned int enb = pmu_cntenset_read ();
    enb &= 1 << pmnx;
    return enb;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- */
/* Disable/Enable a set of event counters, including Cycle Counter        */
/* ---------------------------------------------------------------------- *//*!

  \brief  Disable all of event counters

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmall_cnt_disable ()
{
    pmu_cntenclr_write (PMU_PMNXS_M_ALL);
    return;
}
/* ---------------------------------------------------------------------- */


/* ---------------------------------------------------------------------- *//*!

  \brief  Enable all of event counters

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmall_cnt_enable ()
{
    pmu_cntenset_write (PMU_PMNXS_M_ALL);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Disable a specified set of event counters

  \param[in] pmnxs The set of event counters to disable.  This is a 
                   bit mask, where the valid bit are from 0 - N-1, 
                   where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.  Bit values
                   of 0 are ignored, \i.e. only a 1 causes the counter
                   to be enabled.

  Level: Intermediate

  \note
   Specifying bits representing counters that do not exist is okay. They
   will be ignored by the hardware.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_cnt_disable (unsigned int pmnxs)
{
    pmu_cntenclr_write (pmnxs);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Enable a specified set of event counters

  \param[in] pmnxs The set of event counters to enable.  This is a 
                   bit mask, where the valid bit are from 0 - N-1, 
                   where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.  Bit values
                   of 0 are ignored, \i.e. only a 1 causes the counter
                   to be enabled.

  Level: Intermediate

  \note
   Specifying bits representing counters that do not exist is okay. They
   will be ignored by the hardware.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_cnt_enable (unsigned int pmnxs)
{
    pmu_cntenset_write (pmnxs);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief     Enables \e and disables a specified set of event counters

  \param[in] pmnxs The set of event counters to enable.  This is a 
                   bit mask, where the valid bit are from 0 - N-1, 
                   where N = the number of event counters, 
                   \e e.g. 6 or 31 for the cycle counter.  Bit values
                   of 
                       0 - disables the counter
                       1 - enables  the counter

  Level: Intermediate

  \note
   Specifying bits representing counters that do not exist is okay. They
   will be ignored by the hardware.  

   This routine provides a method to postively set the enable of a counter
   to a known state.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_cnt_enbdsb (unsigned int pmnxs)
{
    pmu_cntenset_write ( pmnxs);
    pmu_cntenclr_write (~pmnxs);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns the set of enabled counters
  \return A bit mask representing the enabled counters.

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_pmnxs_cnt_are_enabled  ()
{
    unsigned int reg = pmu_cntenset_read ();
    return reg;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- */
/* READ/WRITE the CYCLE COUNTER                                           */
/* ---------------------------------------------------------------------- *//*!

  \brief  Reads the number of cycle counts
  \return The number of cycle counts

  Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cycle_cnt_read ()
{
    unsigned int reg = pmu_ccntr_read ();
    return reg;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Writes the number of cycle counts

  \param[in] count The cycle count value

  Level: Intermediate

   This is a fairly weird function.  One possible use would be to set the
   cyclic count register to a value that would cause it to overflow after
   a specified number of counts.  If the overflow count was connected to
   an interrupt routine, one could use this interrupt to trigger some
   other software or hardware event (presuming the interrupts were also
   exported to the hardware event bus.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_cycle_cnt_write (unsigned int count)
{
    pmu_ccntr_write (count);
    return;
}
/* ---------------------------------------------------------------------- */





/* ---------------------------------------------------------------------- */
/* READ/WRITE an INDIVIDUAL EVENT COUNTER                                 */
/* ---------------------------------------------------------------------- *//*!

  \brief  Read the value of the specified event counter
  \return The read value

  \param[in] pmnx  The specified event counter to read.  This must be
                   a value from 0 to N - 1, where N = the number of
                   event counters.  Reads to non-exisitent counters are
                   unpredictable.

  Level: Intermediate

  \warning
   Note that unlike some other methods, 31 does not represent the cycle
   counter.  One must use \sa pmu_cycle_cnt_read for that functionality.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_pmnx_cnt_read (unsigned int pmnx)
{
    pmu_selr_write    (pmnx);
    unsigned int reg = pmu_xevcntr_read ();
    return reg;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Writes the number of counts to the specified event counter.

  \param[in] pmnx  The targetted event counter
  \param[in] count The event count value

   Level: Intermediate

   This is a fairly weird function.  One possible use would be to set the
   counter to a value that would cause it to overflow after a specified 
   number of counts.  If the overflow count was connected to an interrupt
   routine, one could use this interrupt to trigger some other software 
   or hardware event (presuming the interrupts were also exported to the
   hardware event bus.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnx_cnt_write (unsigned int    pmnx,
                                       unsigned int   count)
{
    pmu_selr_write    (pmnx);
    pmu_xevcntr_write (count);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief Uses a bit mask to indicate which counters should be read.  The
         results are placed in the corresponding elements of the output
         \a counts array.  Contrast with the pmu_pmnxs_cnt_dense_read
         which places the read counters in consecutive locations of the
         output \a counts array.

  \param[in]  pmnxs  The bit mask of counters to read, presented with
                     0 = least significant bit.
  \param[out] counts An array to receive the read results. Since the results
                     are placed in the element corresponding to the set
                     bit, this array must be at least the size of the 
                     largest set bit (actually + 1).

   Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_cnt_sparse_read  (unsigned int   pmnxs,
                                               unsigned int *counts)
{
    asm ("rbit %0, %1" : "=r"(pmnxs) : "r"(pmnxs));
    while (pmnxs)
    {
        unsigned int pmnx;
        asm ("clz %0,%1" : "=r"(pmnx) : "r"(pmnxs));
        pmnxs   &=  ~(0x80000000 >> pmnx);
       *counts++ = pmu_pmnx_cnt_read (pmnx);

    }

    return;

}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief Uses a bit mask to indicate which counters should be read.  The
         results are placed in the consecutive elements of the output
         \a counts array.  Contrast with the pmu_pmnxs_cnt_spares_read
         which places the read counters in the element corresponding to
         the set bit number.

  \param[in]  pmnxs  The bit mask of counters to read, presented with
                     0 = least significant bit.
  \param[out] counts An array to receive the read results. Since the 
                     resultsare placed in the consecutive elements, this
                     array must be at least the size of the count of
                     set bits in \pmnxs.

   Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_cnt_dense_read   (unsigned int   pmnxs,
                                               unsigned int *counts)
{
    asm ("rbit %0, %1" : "=r"(pmnxs) : "r"(pmnxs));
    while (pmnxs)
    {
        unsigned int pmnx;
        asm ("clz %0,%1" : "=r"(pmnx) : "r"(pmnxs));
        pmnxs   &=  ~(0x80000000 >>  pmnx);
       *counts++ = pmu_pmnx_cnt_read (pmnx);
    }

    return;

}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Convenience routine to read all six performance monitor counters

  \param[out] counts  The read performance monitor counters

   Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmall_cnt_set_read (unsigned int counts[6])
{
    counts[0] = pmu_pmnx_cnt_read (0);
    counts[1] = pmu_pmnx_cnt_read (1);
    counts[2] = pmu_pmnx_cnt_read (2);
    counts[3] = pmu_pmnx_cnt_read (3);
    counts[4] = pmu_pmnx_cnt_read (4);
    counts[5] = pmu_pmnx_cnt_read (5);

    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Convenience routine to read all six performance monitor counters
          into individually specified locations

  \param[out] count0  Returned as the read counts for performance monitor 0
  \param[out] count1  Returned as the read counts for performance monitor 1
  \param[out] count2  Returned as the read counts for performance monitor 2
  \param[out] count3  Returned as the read counts for performance monitor 3
  \param[out] count4  Returned as the read counts for performance monitor 4
  \param[out] count5  Returned as the read counts for performance monitor 5

   Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmall_cnt_read (unsigned int        *count0,
                                       unsigned int        *count1,
                                       unsigned int        *count2,
                                       unsigned int        *count3,
                                       unsigned int        *count4,
                                       unsigned int        *count5)
{
    *count0 = pmu_pmnx_cnt_read (0);
    *count1 = pmu_pmnx_cnt_read (1);
    *count2 = pmu_pmnx_cnt_read (2);
    *count3 = pmu_pmnx_cnt_read (3);
    *count4 = pmu_pmnx_cnt_read (4);
    *count5 = pmu_pmnx_cnt_read (5);

    return;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Writes an initial value into the counters specified by the 
          \pmnxs bit array.  The values are taken from the \counts elements 
          corresponding to the set bit.  Contrast this with
          pmu_pmnxs_cnt_dense_write with takes the values from consecutive
          locations of the \counts array.

  \param[in]  pmnxs  The bit mask of counters to write, presented with
                     0 = least significant bit.
  \param[out] counts An array holding the counter values to set. Since the
                     values are taken from the element corresponding to 
                     the set bit, this array must be at least the size of
                     the largest set bit (actually + 1).

   Level: Intermediate

   This is a fairly weird function.  One possible use would be to set the
   counter to a value that would cause it to overflow after a specified
   number of counts.  If the overflow count was connected to an interrupt
   routine, one could use this interrupt to trigger some other software 
   or hardware action (presuming the interrupts were also exported to the
   hardware event bus).
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_cnt_sparse_write (unsigned int         pmnxs,
                                               unsigned int const *counts)
{
    asm ("rbit %0, %1" : "=r"(pmnxs) : "r"(pmnxs));
    while (pmnxs)
    {
        unsigned int pmnx;
        asm ("clz %0,%1" : "=r"(pmnx) : "r"(pmnxs));
        pmnxs &=   ~(0x80000000 >> pmnx);
        pmu_selr_write           (pmnx);
        pmu_xevcntr_write (counts[pmnx]);
    }

    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Writes an initial value into the counters specified by the 
          \pmnxs bit array.  The values are taken from consecutive 
          elements of \a counts array. Contrast this with
          pmu_pmnxs_cnt_sparse_write with takes the values from the 
          elements in the \a counts array corresponding to set bit number.

  \param[in]  pmnxs  The bit mask of counters to write, presented with
                     0 = least significant bit.
  \param[out] counts An array holding the counter values to set. Since the
                     values are taken from the element corresponding to 
                     the set bit, this array must be at least the size of
                     the largest set bit (actually + 1).

   Level: Intermediate

   This is a fairly weird function.  One possible use would be to set the
   counter to a value that would cause it to overflow after a specified
   number of counts.  If the overflow count was connected to an interrupt
   routine, one could use this interrupt to trigger some other software 
   or hardware action (presuming the interrupts were also exported to the
   hardware event bus).
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_cnt_dense_write  (unsigned int         pmnxs,
                                               unsigned int const *counts)
{
    asm ("rbit %0, %1" : "=r"(pmnxs) : "r"(pmnxs));
    while (pmnxs)
    {
        unsigned int pmnx;
        asm ("clz %0,%1" : "=r"(pmnx) : "r"(pmnxs));
        pmnxs &= ~(0x80000000 >> pmnx);
        pmu_selr_write          (pmnx);
        pmu_xevcntr_write  (*counts++);
    }

    return;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Writes an initial value into all 6 of the pmnx counters 

  \param[out] counts An array of 6 counter values to set.

   Level: Intermediate

   This is a fairly weird function.  One possible use would be to set the
   counter to a value that would cause it to overflow after a specified
   number of counts.  If the overflow count was connected to an interrupt
   routine, one could use this interrupt to trigger some other software 
   or hardware action (presuming the interrupts were also exported to the
   hardware event bus).

   This function is even weirder, since while one might understand 
   writing to a single counter, writing to all 6??  Really just provided
   for a consistent interface.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmall_cnt_set_write (unsigned int const counts[6])
{
    pmu_pmnx_cnt_write (0, counts[0]);
    pmu_pmnx_cnt_write (1, counts[1]);
    pmu_pmnx_cnt_write (2, counts[2]);
    pmu_pmnx_cnt_write (3, counts[3]);
    pmu_pmnx_cnt_write (4, counts[4]);
    pmu_pmnx_cnt_write (5, counts[5]);

    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Writes an initial value into all 6 of the pmnx counters 

  \param[out] count0 The value to write to performance counter 0
  \param[out] count1 The value to write to performance counter 1
  \param[out] count2 The value to write to performance counter 2
  \param[out] count3 The value to write to performance counter 3
  \param[out] count4 The value to write to performance counter 4
  \param[out] count5 The value to write to performance counter 5

   Level: Intermediate

   This is a fairly weird function.  One possible use would be to set the
   counter to a value that would cause it to overflow after a specified
   number of counts.  If the overflow count was connected to an interrupt
   routine, one could use this interrupt to trigger some other software 
   or hardware action (presuming the interrupts were also exported to the
   hardware event bus).

   This function is even weirder, since while one might understand 
   writing to a single counter, writing to all 6??  Really just provided
   for a consistent interface.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmall_cnt_write (unsigned int count0,
                                        unsigned int count1,
                                        unsigned int count2,
                                        unsigned int count3,
                                        unsigned int count4,
                                        unsigned int count5)
{
    pmu_pmnx_cnt_write (0, count0);
    pmu_pmnx_cnt_write (1, count1);
    pmu_pmnx_cnt_write (2, count2);
    pmu_pmnx_cnt_write (3, count3);
    pmu_pmnx_cnt_write (4, count4);
    pmu_pmnx_cnt_write (5, count5);

    return;
}
/* ---------------------------------------------------------------------- */



 
/* ---------------------------------------------------------------------- */
/* READ/WRITE the overflow flags                                          */
/* ---------------------------------------------------------------------- *//*!

  \brief  Reset/Clear all the overflow flags 

   Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmall_ovr_reset ()
{
    pmu_ovrsr_write (PMU_PMNXS_M_ALL);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Clears the overflow flags of the specified set of counters

  \param[in]  pmnxs  The bit mask of targeted counters

   Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnxs_ovr_reset (unsigned int pmnxs)
{
    unsigned int ovrs = pmu_ovrsr_read ();
    ovrs &= ~pmnxs;
    pmu_ovrsr_write (ovrs);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Read the overflow flags 
  \return A bit mask representing the event counters that have overflowed

   Level: Intermediate
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_pmnxs_ovr_read ()
{
    unsigned int ovrs = pmu_ovrsr_read ();
    return ovrs;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- */
/* SOFTWARE COUNTER INCREMENT                                             */
/* ---------------------------------------------------------------------- *//*!

  \brief Increment the specfied software counter

  \param[in] pmxn  The software counter to increment.  This is one of 
                   the event counters that has been associated with the
                   software increment event.  If it is not, then no
                   action will be performed.

   Level: Intermediate

  \note
   The fundamental operation is to incremewnt a set of event counters,
   \sa pmu_pmnxs_software_increment. If one is only inrementing one 
   counter, using this routine may make that intent clearer.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_pmnx_software_increment  (unsigned int pmnx)
{
    pmu_swinc_write (1 << pmnx);
    return;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief Increment the specfied set of software counters
  
  \param[in] pmxns The set of software counters to increment.  These must
                   be the event counters that has been associated with the
                   software increment event.  If it is not, then no
                   action will be performed.  Therefore, one can specify
                   all the event counters to ensure that all software
                   events that have been associated with an event counter
                   will be incremented.

   Level: Intermediate

  \note
   This is the fundamental hardware operation. However, if only one 
   software counter is being implemented, consider using \sa
   pmu_pmnx_software_increment. This may contribute the readability of
   the code.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void  pmu_pmnxs_software_increment (unsigned int pmnxs)
{
    pmu_swinc_write (pmnxs);
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Resets the values of the six multiplexed counters along with the
          cyclic counter and overflow flags.

   Level: Easy
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_reset ()
{
    pmu_global_cnt_reset();
    pmu_pmall_ovr_reset ();
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Starts all 6 of the multiplexed counters and the cyclic counter

   Level: Easy

  \note
   This routine is a bit heavy handed, first enabling the 6 individual 
   multiplexed counters, then enabling the cyclic counter and the set
   of enabled multiplexed counters.

   Note that there are separate enables for the multiplexed counters,
      - Enables on the individual counters
      - A global enable

   This is likely done for reasons of automacity. In this simple high
   level interface, no distinction is made.  One could imagine a scenario
   whereby a set of 3 multiplexed counters is enabled, the global enable
   set, the disabled, then the other set of 3 multiplexed counters where
   enabled...

   A reasonable use case would be to first enable the set of multiplexed
   counters, then use only the global enables and disables, but this suite
   of routines was designed to be as easy to use as possible.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_start ()
{
    pmu_pmall_cnt_enable  ();
    pmu_global_enable     ();
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Stops all 6 of the multiplexed counters and the cyclic counter

   Level: Easy

  \note
   This routine is a bit heavy handed, first disabling the cyclic 
   counter and the set of enabled multiplexed counters, then disabling
   the 6 individual multiplexed counters.
   of enabled multiplexed counters.

   Note that there are separate disables for the multiplexed counters,
      - disables on the individual counters
      - A global enable

   This is likely done for reasons of automacity. In this simple high
   level interface, no distinction is made.  One could imagine a scenario
   whereby a set of 3 multiplexed counters is enabled, the global enable
   set, the disabled, then the other set of 3 multiplexed counters where
   enabled...

   A reasonable use case would be to first enable the set of 
   multiplexed counters, then use only the global enables and disables,
   but this suite of routines was designed to be as easy to use as 
   possible.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_stop ()
{
    pmu_global_disable    ();
    pmu_pmall_cnt_disable ();
    return;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Reads the cycle counter, the overflow flags and the 6 multiplexed
          counters

  \param[out]  results Filled with the results of the reads

   Level: Easy
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_read (PmuResults *results)
{
    results->cycles    = pmu_cycle_cnt_read (); // Read CCNT
    results->overflow  = pmu_pmnxs_ovr_read (); // Check for overflow flag

    pmu_pmall_cnt_set_read (results->cnt);     // Read all multiplexed counters

    return;
}
/* ---------------------------------------------------------------------- */

#ifdef __cplusplus
}
#endif

#endif
