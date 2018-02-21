// -*-Mode: C;-*-

#ifndef PMU_EID0_H
#define PMU_EID0_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_ceid0.h
  \brief  Provides accesss/interface to the Performance Monitors Common 
          Event ID Register 0
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_ceid0.h $

  \par Credits:
       SLAC

  \verbatim
                               Copyright 2013
                                    by
                       The Board of Trustees of the
                    Leland Stanford Junior University.
                           All rights reserved.
  \endverbatim

  \par Common Event Identifiers
   The ARM architecture designates event identifiers 0 - 0x3F as the common
   event identifiers.  This are reserved for the specified events. When an 
   ARMv7 processor supports monitoring of an event that is assigned a number
   in this range, if possible it must use that number for the event. 
   Unassigned values are reserved and might be used for additional common
   events in future versions of the architecture.

   The PMCCEID0 register is a read-only register that identifies which of
   the common event identifiers are actually implemented. This value is
   returned as a 32-bit mask.

  \warning
   While a great idea, in the ZNYQ, this register appears to always read
   as 0.
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


#define M(val) (1 << (val))

/* ---------------------------------------------------------------------- */
/* REGISTER ACCESS: Performance Monitor CEID0 and EID1 Register            */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_ceid0_read ();

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum   _PMU_CEID0_K
  \brief   Enumerates the common event identifiers in the range 0x00 - 0x1F
           that can be monitored
                                                                          *//*!
  \typedef PMU_CEID0_K
  \brief   Typedef for enum _PMU_CEID0_K
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_CEID0_K
{
    PMU_CEID0_K_SW_INCR               = 0x00,/*!< Instruction architecturally
                                                  executed, condition code
                                                  check pass, software 
                                                  increment                  */
    PMU_CEID0_K_L1I_CACHE_REFILL      = 0x01,/*!< Level 1 instruction cache 
                                                 refill                      */
    PMU_CEID0_K_L1I_TLB_REFILL        = 0x02,/*!< Level 1 instruction TLB 
                                                 refill                      */
    PMU_CEID0_K_L1D_CACHE_REFILL      = 0x03,/*!< Level 1 data cache refill  */
    PMU_CEID0_K_L1D_CACHE             = 0x04,/*!< Level 1 data cache access  */
    PMU_CEID0_K_L1D_TLB_REFILL        = 0x05,/*!< Level 1 data TLB refill    */
    PMU_CEID0_K_LD_RETIRED            = 0x06,/*!< Instruction architecturally  
                                                   executed, condition code 
                                                  check pass, load           */
    PMU_CEID0_K_ST_RETIRED            = 0x07,/*!< Instruction architecturally
                                                  executed, condition code 
                                                  check pass, store          */
    PMU_CEID0_K_INST_RETIRED          = 0x08,/*!< Instruction architecturally 
                                                  executed                   */
    PMU_CEID0_K_EXC_TAKEN             = 0x09,/*!< Exception taken            */
    PMU_CEID0_K_EXC_RETURN            = 0x0a,/*!< Instruction architecturally
                                                  executed, exception return */
    PMU_CEID0_K_CID_WRITE_RETIRED     = 0x0b,/*!< Instruction architecturally 
                                                  executed, condition code 
                                                  check pass, write to 
                                                  CONTEXTIDR                 */
    PMU_CEID0_K_PC_WRITE_RETIRED      = 0x0c,/*!< Instruction architecturally
                                                  executed, condition code 
                                                  check pass, software change
                                                  of the PC                  */
    PMU_CEID0_K_BR_IMMED_RETIRED      = 0x0d,/*!< Instruction architecturally
                                                  executed, immediate branch */
    PMU_CEID0_K_BR_RETURN_RETIRED     = 0x0e,/*!< Instruction architecturally
                                                  executed, condition code
                                                  check pass, procedure 
                                                  return                     */
    PMU_CEID0_K_UNALIGNED_LDST_RETIRED= 0x0f,/*!< Instruction architecturally
                                                  executed, condition code
                                                  check pass, unaligned load
                                                  or store                   */
    PMU_CEID0_K_BR_MIS_PRED           = 0x10,/*!< Mispredicted or not
                                                  predicted branch
                                                  speculatively executed     */


    PMU_CEID0_K_CPU_CYCLES            = 0x11,/*!< Cycle                      */
    PMU_CEID0_K_BR_PRED               = 0x12,/*!< Predictable branch 
                                                  speculatively executed     */
    PMU_CEID0_K_MEM_ACCESS            = 0x13,/*!< Data memory access         */
    PMU_CEID0_K_L1I_CACHE             = 0x14,/*!< Level 1 instruction cache
                                                  access                     */
    PMU_CEID0_K_L1D_CACHE_WB          = 0x15,/*!< Level 1 data cache 
                                                  write-back                 */
    PMU_CEID0_K_L2D_CACHE             = 0x16,/*!< Level 2 data cache access  */
    PMU_CEID0_K_L2D_CACHE_REFILL      = 0x17,/*!< Level 2 data cache refill  */
    PMU_CEID0_K_L2D_CACHE_WB          = 0x18,/*!< Level 2 data cache 
                                                  write-back                 */
    PMU_CEID0_K_BUS_ACCESS            = 0x19,/*!< Bus access                 */
    PMU_CEID0_K_MEMORY_ERROR          = 0x1a,/*!< Local memory error         */
    PMU_CEID0_K_INST_SPEC             = 0x1b,/*!< Instruction speculatively 
                                                  executed                   */
    PMU_CEID0_K_TTBR_WRITE_RETIRED    = 0x1c,/*!< Instruction architecturally
                                                  executed, condition code
                                                  check pass, write to TTBR  */
    PMU_CEID0_K_BUS_CYCLES            = 0x1d,/*!< Bus cycle                  */
    PMU_CEID0_K_RSVD_0x1E             = 0x1e,
    PMU_CEID0_K_RSVD_0x1F             = 0x1f,
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_CEID0_K_TD
#define       PMU_CEID0_K_TD
typedef enum _PMU_CEID0_K PMU_CEID0_K;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum   _PMU_CEID0_M
  \brief   Enumerates the event identifiers that can be monitored
                                                                          *//*!
  \typedef PMU_CEID0_M
  \brief   Typedef for enum _PMU_CEID0_M

  \par Event Numbers
   The event numbers are split into two ranges

     - 0x00-0x3f  Common features. Reserved for the specified evnts. When
                  an ARMv7 processor supports monitoring of an event that
                  is assigned a number in this range, if possible it must
                  use that number for the event. Unassigned values are
                  reserved and might be used of additional common events
                  in future versions of the architecture.

    - 0x40-0xFF   \e IMPLEMENTATION DEFINED features.
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_CEID0_M
{
    PMU_CEID0_M_SW_INCR               = M( 0),/*!< Instruction architecturally
                                                   executed, condition code
                                                   check pass, software 
                                                   increment                 */
    PMU_CEID0_M_L1I_CACHE_REFILL      = M( 1),/*!< Level 1 instruction cache 
                                                   refill                    */
    PMU_CEID0_M_L1I_TLB_REFILL        = M( 2),/*!< Level 1 instruction TLB 
                                                   refill                    */
    PMU_CEID0_M_L1D_CACHE_REFILL      = M( 3),/*!< Level 1 data cache refill */
    PMU_CEID0_M_L1D_CACHE             = M( 4),/*!< Level 1 data cache access */
    PMU_CEID0_M_L1D_TLB_REFILL        = M( 5),/*!< Level 1 data TLB refill   */
    PMU_CEID0_M_LD_RETIRED            = M( 6),/*!< Instruction 
                                                   architecturally executed,
                                                   condition code check pass,
                                                   load                      */
    PMU_CEID0_M_ST_RETIRED            = M( 7),/*!< Instruction architecturally
                                                   executed, condition code 
                                                   check pass, store         */
    PMU_CEID0_M_INST_RETIRED          = M( 8),/*!< Instruction architecturally 
                                                   executed                  */
    PMU_CEID0_M_EXC_TAKEN             = M( 9),/*!< Exception taken           */
    PMU_CEID0_M_EXC_RETURN            = M(10),/*!< Instruction architecturally
                                                   executed, exception return*/
    PMU_CEID0_M_CID_WRITE_RETIRED     = M(11),/*!< Instruction architecturally 
                                                   executed, condition code 
                                                   check pass, write to 
                                                   CONTEXTIDR                */
    PMU_CEID0_M_PC_WRITE_RETIRED      = M(12),/*!< Instruction architecturally
                                                   executed, condition code 
                                                   check pass, software change
                                                   of the PC                 */
    PMU_CEID0_M_BR_IMMED_RETIRED      = M(13),/*!< Instruction architecturally
                                                   executed, immediate branch*/
    PMU_CEID0_M_BR_RETURN_RETIRED     = M(14),/*!< Instruction architecturally
                                                   executed, condition code
                                                   check pass, procedure
                                                   return                    */
    PMU_CEID0_M_UNALIGNED_LDST_RETIRED= M(15),/*!< Instruction architecturally
                                                   executed, condition code
                                                   check pass, unaligned load
                                                   or store                  */
    PMU_CEID0_M_BR_MIS_PRED           = M(16),/*!< Mispredicted or not
                                                   predicted branch
                                                   speculatively executed    */


    PMU_CEID0_M_CPU_CYCLES            = M(17),/*!< Cycle                     */
    PMU_CEID0_M_BR_PRED               = M(18),/*!< Predictable branch 
                                                   speculatively executed    */
    PMU_CEID0_M_MEM_ACCESS            = M(19),/*!< Data memory access        */
    PMU_CEID0_M_L1I_CACHE             = M(20),/*!< Level 1 instruction cache
                                                   access                    */
    PMU_CEID0_M_L1D_CACHE_WB          = M(21),/*!< Level 1 data cache 
                                                   write-back                */
    PMU_CEID0_M_L2D_CACHE             = M(22),/*!< Level 2 data cache access */
    PMU_CEID0_M_L2D_CACHE_REFILL      = M(23),/*!< Level 2 data cache refill */
    PMU_CEID0_M_L2D_CACHE_WB          = M(24),/*!< Level 2 data cache 
                                                   write-back                */
    PMU_CEID0_M_BUS_ACCESS            = M(25),/*!< Bus access                */
    PMU_CEID0_M_MEMORY_ERROR          = M(26),/*!< Local memory error        */
    PMU_CEID0_M_INST_SPEC             = M(27),/*!< Instruction speculatively 
                                                   executed                  */
    PMU_CEID0_M_TTBR_WRITE_RETIRED    = M(28),/*!< Instruction architecturally
                                                   executed, condition code
                                                   check pass, write to TTBR */
    PMU_CEID0_M_BUS_CYCLES            = M(29),/*!< Bus cycle                 */
    PMU_CEID0_M_RSVD_0x1E             = M(30),
    PMU_CEID0_M_RSVD_0x1F             = M(31),
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_CEID0_M_TD
#define       PMU_CEID0_M_TD
typedef enum _PMU_CEID0_M PMU_CEID0_M;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Primitive to read PMCEID0, the Performance Monitor Event 
          Identification register 0.

  \return The value of the Performance Monitor Event Identification 
          register 0.

   The PMCCEID0 register defines which the first common architectural 
   and common micro architectural feature events are implemented. See 
   \sa enum _PMU_CEID0_K and \sa enum _PMU_CEID0_M for the definition of the 
    events.  This value is returned as a bit mask.

  \warning
   This is only provided for completeness. On the ZYNQ version of the
   ARM, this register appears not to be implemented.  It always returns 0.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_ceid0_read ()
{
    unsigned int reg;
    asm volatile (" MRC     p15, 0, %0, c9, c12, 6" : "=r"(reg) ::);
    return reg;
}
/* ---------------------------------------------------------------------- */


#undef M

#ifdef __cplusplus
}
#endif

#endif
