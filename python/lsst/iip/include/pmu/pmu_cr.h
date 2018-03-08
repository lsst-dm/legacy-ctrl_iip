// -*-Mode: C;-*-

#ifndef PMU_CR_H
#define PMU_CR_H

/* ---------------------------------------------------------------------- *//*!

  \file   pmu_cr.h
  \brief  Provides access/interface to the Performance Monitor Control
           Register
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
      \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_cr.h $

  \par Credits:
        SLAC

  \verbatim
                               Copyright 2013
                                    by
                       The Board of Trustees of the
                    Leland Stanford Junior University.
                           All rights reserved.
  \endverbatim

  \par Purpose
   The PMCR provides details of the Performance Monitor implementation,
   including the number of counters implemented and configures and
   controls the counters

  \par Layout

  \verbatim

    |31    24|23    16|15 12|11      6|5|4|3|2|1|0|
    +--------+--------+-----+---------+-+-+-+-+-+-+
    |  IMP   | IDCODE |  N  |   Rsvd  |D|X|D|C|P|E|
    |        |        |     | UNK/SBZP|P| | | | | |
    +--------+--------+-----+---------+-+-+-+-+-+-+

  \endverbatim

    where
     - IMP     = Implementater code. This field is read-only with an
                 implementation defined value. 
     - IDCODE  = Identification code.  This field is read-only with an
                 implementation defined value. A specific implementation
                 is identified by the combination of the implementer code
                 and the identification code.
     - N       = Number of event counters. This field is read-only with an
                 implementation defined value that indicates the number of
                 counters implemented.
     - DP      = Disable the PMCCNTR when event counting is prohibited.
                 The possible values of this bit are
                   - 0 Cycle counter operates regardless of the 
                       non-invasion debug authentication settings
                   - 1 Cycle counter is disabled if non-invasive debug
                       is not prohibited.
     - X       = Export enable. The possible values are
                   - 0 Export of events is disabled
                   - 1 Export of events is enabled
                 This bit enables the exporting of events to another debug
                 device, such as trace macrocell over an event bus. If the
                 implementation does not include such an event bus, this 
                 bit is RAZ/WI.
                 This bit does not affect the generation of Performance
                 Monitors interrupts, that can be implemented as a signal
                 exported for the processor to the interrupt controller.
                 This bit is R/W. Its non-debug logic reset value is 0.
    - D        = Cycle Counter Divider. The possible values of this bit
                 are:
                   - 0 When enabled, the PMCCNTR counts every clock cycle.
                   - 1 When enabled, the PMCCNTR counts event 64 clock
                       cycles
    - C        = Cycle Counter Reset.This bit is write-only. The effects
                 of writing to this bit are:
                   - 0 No action
                   - 1 Reset PMCCNTR to zero
    - P        = Event counter reset. This bit is write-only. The effects
                 of writing to this bit are:
                   - 0 No action
                   - 1 Reset all event counters, not include PMCCNTR, to
                       zero.
    - E        = Enable. The possible value of this bit are:
                   - 0 All counters, including PMCCNTR and disabled
                   - 1 All counters, are enabled.   
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


#include <stdio.h>
#include "pmu/pmu_common.h"


#ifdef __cplusplus
extern "C"
{
#endif


/* ---------------------------------------------------------------------- */
/* REGISTER ACCESS: Performance Monitor Control Register                  */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_cr_read               ();
static void         pmu_cr_write              (unsigned int    cr);


static unsigned int pmu_cr_enable_get         (unsigned int   cr);
static unsigned int pmu_cr_cycle_div64_get    (unsigned int   cr);
static unsigned int pmu_cr_export_get         (unsigned int   cr);
static unsigned int pmu_cr_cycle_prohibit_get (unsigned int   cr);
static unsigned int pmu_cr_ncounters_get      (unsigned int   cr);
static unsigned int pmu_cr_idcode_get         (unsigned int   cr);
static unsigned int pmu_cr_imp_get            (unsigned int   cr);


static unsigned int pmu_cr_enable_set         (unsigned int   cr, 
                                               unsigned int flag);
static unsigned int pmu_cr_pmnxs_reset_set    (unsigned int   cr,
                                               unsigned int flag);
static unsigned int pmu_cr_cycle_reset_set    (unsigned int   cr,
                                               unsigned int flag);
static unsigned int pmu_cr_cycle_div64_set    (unsigned int   cr,
                                               unsigned int flag);
static unsigned int pmu_cr_export_set         (unsigned int   cr,
                                               unsigned int flag);
static unsigned int pmu_cr_cycle_prohibit_set (unsigned int   cr,
                                               unsigned int flag);
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_CR_S
  \brief    Maps out the sizes of the bit fields in the Performance
            Monitor Control Register, PMCR.
                                                                          *//*!
  \typedef  PMU_CR_S
  \brief    Typedef for enum _PMU_CR_S
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_CR_S
{
    PMU_CR_S_E              = 1,  /*!< Enable/Disable all counters, 
                                       including the PMCCNTR              */
    PMU_CR_S_P              = 1,  /*!< Reset all counters, not including
                                       the PMCCNTR, to zero. This is a
                                       write-only bit                     */
    PMU_CR_S_C              = 1,  /*!< Reset the cycle counter, PMCCNTR
                                       to zero. This is a write-only bit  */
    PMU_CR_S_D              = 1,  /*!< Cycle counter divide by 64 bit     */
    PMU_CR_S_X              = 1,  /*!< Enable/Diable the exporting of
                                       events to the event bus            */
    PMU_CR_S_DP             = 1,  /*!< Disable PMCCNTR when event
                                       counting in prohibited.            */
    PMU_CR_S_RSVD           = 5,  /*!< Reserved, UJNK/SBZP                */
    PMU_CR_S_N              = 5,  /*!< Number of event counters.  If 0,
                                       only the Cycle Count Register is
                                       implemented. 
                                       This field is read-only.           */
    PMU_CR_S_IDCODE         = 8,  /*!< Implementer identifier.
                                       This field is read-only.           */
    PMU_CR_S_IMP            = 8,  /*!< Implementer code
                                       This field is read-only.           */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_CR_S_TD
#define       PMU_CR_S_TD
typedef enum _PMU_CR_S PMU_CR_S;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_CR_V
  \brief    Maps out the right-justified shift of the bit fields in the
            Performance Monitor Control Register, PMCR
                                                                          *//*!
  \typedef  PMU_CR_V
  \brief    Typedef for enum _PMU_CR_V
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_CR_V
{
    PMU_CR_V_E              =  0, /*!< Enable/Disable all counters, 
                                       including the PMCCNTR              */
    PMU_CR_V_P              =  1, /*!< Reset all counters, not including
                                       the PMCCNTR, to zero. This is a
                                       write-only bit                     */
    PMU_CR_V_C              =  2, /*!< Reset the cycle counter, PMCCNTR
                                       to zero. This is a write-only bit  */
    PMU_CR_V_D              =  3, /*!< Cycle counter divide by 64 bit     */
    PMU_CR_V_X              =  4, /*!< Enable/Diable the exporting of
                                       events to the event bus            */
    PMU_CR_V_DP             =  5, /*!< Disable PMCCNTR when event
                                       counting in prohibited.            */
    PMU_CR_V_RSVD           =  6, /*!< Reserved, UJNK/SBZP                */
    PMU_CR_V_N              = 11, /*!< Number of event counters.  If 0,
                                       only the Cycle Count Register is
                                       implemented. 
                                       This field is read-only.           */
    PMU_CR_V_IDCODE         = 16, /*!< Implementer identifier.
                                       This field is read-only.           */
    PMU_CR_V_IMP            = 24, /*!< Implementer code
                                       This field is read-only.           */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_CR_V_TD
#define       PMU_CR_V_TD
typedef enum _PMU_CR_V PMU_CR_V;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_CR_M
  \brief    Maps out the in-place masks of the bit fields in the
            Performance Monitor Control Register, PMCR.
                                                                          *//*!
  \typedef  PMU_CR_M
  \brief    Typedef for enum _PMU_CR_M
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_CR_M
{
    PMU_CR_M_E              = 0x00000001, /*!< Enable/Disable all counters, 
                                               including the PMCCNTR      */
    PMU_CR_M_P              = 0x00000002, /*!< Reset all counters, not 
                                               including the PMCCNTR, to 
                                               zero. 
                                               This is a write-only bit   */
    PMU_CR_M_C              = 0x00000004, /*!< Reset the cycle counter, 
                                               PMCCNTRto zero. 
                                               This is a write-only bit   */
    PMU_CR_M_D              = 0x00000008, /*!< Cycle counter divide by 64 
                                               bit                        */
    PMU_CR_M_X              = 0x00000010, /*!< Enable/Diable the exporting
                                               of events to the event bus.*/
    PMU_CR_M_DP             = 0x00000020, /*!< Disable PMCCNTR when event
                                               counting in prohibited.    */
    PMU_CR_M_RSVD           = 0x000007C0, /*!< Reserved, UJNK/SBZP        */
    PMU_CR_M_N              = 0x0000F800, /*!< Number of event counters.
                                               If 0, only the Cycle Count
                                               Register is implemented. 
                                               This field is read-only.   */
    PMU_CR_M_IDCODE         = 0x00FF0000, /*!< Implementer identifier.
                                               This field is read-only.   */
    PMU_CR_M_IMP            = 0xFF000000  /*!< Implementer code
                                               This field is read-only.   */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_CR_M_TD
#define       PMU_CR_M_TD
typedef enum _PMU_CR_M PMU_CR_M;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief   Primitive to read PMCR, the Performance Monitor Control
           Register.
  \return  The value of the Performance Monitor Control Register
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_read ()
{
    unsigned int reg;
    asm volatile (" MRC     p15, 0, %0, c9, c12, 0" : "=r"(reg) ::);
    return reg;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief     Primitive to write PMCR, the Performance Monitor Control
             Register.

  \param[in] value  The value to write
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_cr_write (unsigned int       value)
{
    asm volatile (" MCR     p15, 0, %0, c9, c12, 0" :: "r"(value) :);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief       Return the state of the (global) enable bit
  \retval == 0 Global counter enable is disabled
  \retval == 1 Global counter enable is enabled

  \param[in] cr The Performance Monitor Control Register
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_enable_get (unsigned int cr)
{
    return pmu_extract (cr, PMU_CR_V_E, PMU_CR_M_E);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief       Return the state of the divide 64 bit
  \retval == 0 The cycle counter is not divided by 64
  \retval == 1 The cycle counter is divided by 64

  \param[in] cr The Performance Monitor Control Register
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_cycle_div64_get (unsigned int cr)
{
    return pmu_extract (cr, PMU_CR_V_D, PMU_CR_M_D);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief       Return the state of the export bit
  \retval == 0 The events are not exported to the event bus.
  \retval == 1 The events are exported to the event bus.

  \param[in] cr The Performance Monitor Control Register
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_export_get (unsigned int cr)
{
    return pmu_extract (cr, PMU_CR_V_E, PMU_CR_M_E);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief       Return the state of the disable cycle counter when event 
               counting is prohibited
  \retval == 0 The cycle counter operates regardless of the non-invasive
               debug authentication settings
  \retval == 1 The cycle counter is disabled if non-invasive debug is
               no permitted.

  \param[in] cr The Performance Monitor Control Register
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_cycle_prohibit_get (unsigned int cr)
{
    return pmu_extract (cr, PMU_CR_V_DP, PMU_CR_M_DP);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Return the number event counters.
  \return The number of event counters.

  \param[in] cr The Performance Monitor Control Register

  \note
   On the ARMv7 this is 6, but the architecture provides a means of 
   discovering this number independent of the architecture version.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_ncounters_get (unsigned int cr)
{
    return pmu_extract (cr, PMU_CR_V_N, PMU_CR_M_N);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Return the identification code
  \return The identification code. 
          
  \param[in] cr The Performance Monitor Control Register

  \note
   Each implementer maintains a list of identification codes that is 
   specific to the implementer. A specific implementation is identified
   by the combination of the implementer code and this identification
   code.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_idcode_get (unsigned int cr)
{
    return pmu_extract (cr, PMU_CR_V_IDCODE, PMU_CR_M_IDCODE);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Return the implementer code
  \return The implemente code. 
          
  \param[in] cr The Performance Monitor Control Register

  \note
   The implementer codes are allocated by ARM. Thus a specific 
   implementation is identified by the combination of this implementer
   code and the identification code.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_imp_get (unsigned int cr)
{
    return pmu_extract (cr, PMU_CR_V_IMP, PMU_CR_M_IMP);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the state of the (global) enable  bit
  \return The new value of the Performance Monitor Control Register

  \param[in] cr    The Performance Monitor Control Register
  \param[in] flag  The new state of the enable bit
                     - 0 All counters, including the PMCCNTR are disabled
                     - 1 All counters are enabled.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_enable_set (unsigned int   cr, 
                                              unsigned int flag)
{
    cr = pmu_insert (cr, flag, PMU_CR_V_E, PMU_CR_M_E);
    return cr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the state of the event counters reset
  \return The new value of the Performance Monitor Control Register

  \param[in] cr    The Performance Monitor Control Register
  \param[in] flag  The new state of the event counters reset bit
                     - 0 No action
                     - 1 Reset all event counters, not including the
                         cycle counter to zero.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_pmnxs_reset_set (unsigned int   cr,
                                                   unsigned int flag)
{
    cr = pmu_insert (cr, flag, PMU_CR_V_P, PMU_CR_M_P);
    return cr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the state of the cycle counter reset
  \return The new value of the Performance Monitor Control Register

  \param[in] cr    The Performance Monitor Control Register
  \param[in] flag  The new state of the cycle counter reset bit
                     - 0 No action
                     - 1 Reset the cycle counter to zero
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_cycle_reset_set (unsigned int   cr,
                                                   unsigned int flag)
{
    cr = pmu_insert (cr, flag, PMU_CR_V_C, PMU_CR_M_C);
    return cr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the state of the divide cycle counter by 64 bit
  \return The new value of the Performance Monitor Control Register

  \param[in] cr    The Performance Monitor Control Register
  \param[in] flag  The new state of the divide cycle counter by 64 bit
                     - 0 When enabled, the cycle counter counts 
                         every clock cycle.
                     - 1 When enabled, the cycle counter counts
                         every 64 clock cycles.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_cycle_div64_set (unsigned int   cr,
                                                   unsigned int flag)
{
    cr = pmu_insert (cr, flag, PMU_CR_V_D, PMU_CR_M_D);
    return cr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

 \brief  Sets the state of the export enable bit
 \return The new value of the Performance Monitor Control Register

  \param[in] cr    The Performance Monitor Control Register
  \param[in] flag  The new state of the export enable bit
                     - 0 Export of events is disabled
                     - 1 Export of events is enabled
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_export_set   (unsigned int   cr,
                                                unsigned int flag)
{
    cr = pmu_insert (cr, flag, PMU_CR_V_X, PMU_CR_M_X);
    return cr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

 \brief  Sets the state of the disable cycle counting prohibit bit
 \return The new value of the Performance Monitor Control Register

  \param[in] cr    The Performance Monitor Control Register
  \param[in] flag  The new state of the disable cycle counting prohibit bit
                     - 0 Cycle counter operates regardless of the 
                         non-invasive debug authenication settings
                     - 1 Cycle counter is disabled if non-invasive debug
                         in not permitted.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_cr_cycle_prohibit_set (unsigned int   cr,
                                                      unsigned int flag)
{
    cr = pmu_insert (cr, flag, PMU_CR_V_DP, PMU_CR_M_DP);
    return cr;
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif

#endif
