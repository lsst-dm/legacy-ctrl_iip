// -*-Mode: C;-*-

#ifndef PMU_EID_H
#define PMU_EID_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_eid.h
  \brief  Enumerates the event types that can be counted by the 
          Performance Monitors Unit
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_eid.h $

  \par Credits:
       SLAC

  \verbatim
                               Copyright 2013
                                    by
                       The Board of Trustees of the
                    Leland Stanford Junior University.
                           All rights reserved.
  \endverbatim

  \par Event Identifiers

   While only events 6 can be monitored/counted at any given time, these
   6 events can be selected from a palette of \e<event identifiers> 
   enumerated here.  The numbering space for these \e<event identifiers> 
   are broken into two pieces

       - 0x00-0x3F Common features. Reserved for the specified events. 
                   When an ARMv7 processor supports monitoring of an event
                   that is assigned a number in this range, if possible 
                   it must use that number for the event. Unassigned 
                   values are reserved and might be used for additional
                   common events in future versions of the architecture.

       - 0x40-0xFF IMPLEMENTATION DEFINED features.
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



/* ---------------------------------------------------------------------- *//*!

  \enum   _PMU_EID_K
  \brief   Enumerates the event identifiers that can be monitored
                                                                          *//*!
  \typedef PMU_EID_K
  \brief   Typedef for enum _PMU_EID_K

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
enum _PMU_EID_K
{
    PMU_EID_K_SW_INCR               = 0x00, /*!< Instruction architecturally
                                                 executed, condition code
                                                 check pass, software 
                                                 increment                   */
    PMU_EID_K_L1I_CACHE_REFILL      = 0x01, /*!< Level 1 instruction cache 
                                                 refill                      */
    PMU_EID_K_L1I_TLB_REFILL        = 0x02, /*!< Level 1 instruction TLB 
                                                 refill                      */
    PMU_EID_K_L1D_CACHE_REFILL      = 0x03, /*!< Level 1 data cache refill   */
    PMU_EID_K_L1D_CACHE             = 0x04, /*!< Level 1 data cache access   */
    PMU_EID_K_L1D_TLB_REFILL        = 0x05, /*!< Level 1 data TLB refill     */
    PMU_EID_K_LD_RETIRED            = 0x06, /*!< Instruction architecturally   
                                                 executed, condition code 
                                                 check pass, load            */
    PMU_EID_K_ST_RETIRED            = 0x07, /*!< Instruction architecturally
                                                 executed, condition code 
                                                 check pass, store           */
    PMU_EID_K_INST_RETIRED          = 0x08, /*!< Instruction architecturally 
                                                 executed                    */
    PMU_EID_K_EXC_TAKEN             = 0x09, /*!< Exception taken             */
    PMU_EID_K_EXC_RETURN            = 0x0a, /*!< Instruction architecturally
                                                 executed, exception return  */
    PMU_EID_K_CID_WRITE_RETIRED     = 0x0b, /*!< Instruction architecturally 
                                                 executed, condition code 
                                                 check pass, write to 
                                                 CONTEXTIDR                  */
    PMU_EID_K_PC_WRITE_RETIRED      = 0x0c, /*!< Instruction architecturally
                                                 executed, condition code 
                                                 check pass, software change
                                                 of the PC                   */
    PMU_EID_K_BR_IMMED_RETIRED      = 0x0d, /*!< Instruction architecturally
                                                 executed, immediate branch  */
    PMU_EID_K_BR_RETURN_RETIRED     = 0x0e, /*!< Instruction architecturally
                                                 executed, condition code
                                                 check pass, procedure return*/
    PMU_EID_K_UNALIGNED_LDST_RETIRED= 0x0f, /*!< Instruction architecturally
                                                 executed, condition code
                                                 check pass, unaligned load
                                                 or store                    */
    PMU_EID_K_BR_MIS_PRED           = 0x10, /*!< Mispredicted or not
                                                 predicted branch
                                                 speculatively executed      */


    PMU_EID_K_CPU_CYCLES            = 0x11, /*!< Cycle                       */
    PMU_EID_K_BR_PRED               = 0x12, /*!< Predictable branch 
                                                 speculatively executed      */
    PMU_EID_K_MEM_ACCESS            = 0x13, /*!< Data memory access          */
    PMU_EID_K_L1I_CACHE             = 0x14, /*!< Level 1 instruction cache
                                                 access                      */
    PMU_EID_K_L1D_CACHE_WB          = 0x15, /*!< Level 1 data cache 
                                                  write-back                 */
    PMU_EID_K_L2D_CACHE             = 0x16, /*!< Level 2 data cache access   */
    PMU_EID_K_L2D_CACHE_REFILL      = 0x17, /*!< Level 2 data cache refill   */
    PMU_EID_K_L2D_CACHE_WB          = 0x18, /*!< Level 2 data cache 
                                                 write-back                  */
    PMU_EID_K_BUS_ACCESS            = 0x19, /*!< Bus access                  */
    PMU_EID_K_MEMORY_ERROR          = 0x1a, /*!< Local memory error          */
    PMU_EID_K_INST_SPEC             = 0x1b, /*!< Instruction speculatively 
                                                 executed                    */
    PMU_EID_K_TTBR_WRITE_RETIRED    = 0x1c, /*!< Instruction architecturally
                                                 executed, condition code
                                                 chek pass, write to TTBR    */
    PMU_EID_K_BUS_CYCLES            = 0x1d, /*!< Bus cycle                   */
    PMU_EID_K_RSVD_0x1E             = 0x1e,
    PMU_EID_K_RSVD_0x1F             = 0x1f,



    /* ---------------------------------------------------------------------- */
    /* CORTEX A( ARCHITECTURALLY DEPENDENT COUNTERS                           */
    /* ---------------------------------------------------------------------- */


    /* ---------------------------------------------------------------------- */
    /* 0x40 - 0x4F                                                            */
    /* ---------------------------------------------------------------------- */
    PMU_EID_K_JAVA_BYTECODE_EXE     = 0x40, 
    /*!< Counts the number Java bytecodes being decoded, including 
         spectulative one                                        Approximate  */

    PMU_EID_K_JAVA_BYTECOCE_SW_EXE  = 0x41, 
    /*!< Counts the number of software java bytecodes being decoded, 
         including speculative ones.                             Approximate  */

    PMU_EID_K_JAZELLE_BRANCH_BW_EXE = 0x42,
    /*!< Counts the number of Jazelle taken branches being executed. 
         This includes the branches that are flushed because of a previous
         load/store which aborts late.                           Approximate  */

    PMU_EID_K_RSVD_0x43             = 0x43,
    PMU_EID_K_RSVD_0x44             = 0x44,
    PMU_EID_K_RSVD_0x45             = 0x45,
    PMU_EID_K_RSVD_0x46             = 0x46,
    PMU_EID_K_RSVD_0x47             = 0x47,
    PMU_EID_K_RSVD_0x48             = 0x48,
    PMU_EID_K_RSVD_0x49             = 0x49,
    PMU_EID_K_RSVD_0x4A             = 0x4a,
    PMU_EID_K_RSVD_0x4B             = 0x4b,
    PMU_EID_K_RSVD_0x4C             = 0x4c,
    PMU_EID_K_RSVD_0x4D             = 0x4d,
    PMU_EID_K_RSVD_0x4E             = 0x4e,
    PMU_EID_K_RSVD_0x4F             = 0x4f,
    /* ---------------------------------------------------------------------- */




    /* ---------------------------------------------------------------------- */
    /* 0x50 - 0x5F                                                            */
    /* ---------------------------------------------------------------------- */
    PMU_EID_K_LINEFILL_COHERENT_MISS= 0x50,
    /*!< Counts the number of coherent linefill requests performed by the 
         Cortex-A9 processor which also miss in all the other Cortex-A9
         processors, meaning that the request is sent to the external 
         memory.                                                      Precise */

    PMU_EID_K_LINEFILL_COHERENT_HIT = 0x51, 
    /*!< Counts the number of coherent linefill requests performed by the 
         Cortex-A9 processor which hit in another Cortex-A9 processor, 
         meaning that the linefill data is fetched directly from the
         relevant Cortex-A9 cache.                                   Precise  */

    PMU_EID_K_RSVD_0x53             = 0x53,
    PMU_EID_K_RSVD_0x54             = 0x54,
    PMU_EID_K_RSVD_0x55             = 0x55,
    PMU_EID_K_RSVD_0x56             = 0x56,
    PMU_EID_K_RSVD_0x57             = 0x57,
    PMU_EID_K_RSVD_0x58             = 0x58,
    PMU_EID_K_RSVD_0x59             = 0x59,
    PMU_EID_K_RSVD_0x5A             = 0x5a,
    PMU_EID_K_RSVD_0x5B             = 0x5b,
    PMU_EID_K_RSVD_0x5C             = 0x5c,
    PMU_EID_K_RSVD_0x5D             = 0x5d,
    PMU_EID_K_RSVD_0x5E             = 0x5e,
    PMU_EID_K_RSVD_0x5F             = 0x5f,
    /* ---------------------------------------------------------------------- */




    /* ---------------------------------------------------------------------- */
    /*  0x60 - 0x6F                                                           */
    /* ---------------------------------------------------------------------- */
    PMU_EID_K_STALL_CYCLES_INSTRUCTION = 0x60,
    /*!< Counts the number of cycles where the processor is ready to accept
         new instructions, but does not receive any because of the 
         instruction side not being able to provide any and the instruction
         cache is currently performing at least one linefill.     Approximate */


    PMU_EID_K_STALL_CYCLES_DATA       = 0x61,
    /*!< Counts the number of cycles where the core has some instructions
         that it cannot issue to any pipeline, and the Load Store unit has
         at least one pending linefill request, and no pending TLB requests.
                                                                  Approximate */

    PMU_EID_K_STALL_CYCLES_TLB_MAIN   = 0x62,
    /*! Counts the number of cycles where the processor is stalled waiting
        for the completion of translation table walks from the main TLB. 
        The processor stalls can be because of the instruction side not being
        able to provide the instructions, or to the data side not being able
        to provide the necessary data, because of them waiting for the main
        TLB translation table walk to complete.                    Appoximate */

    PMU_EID_K_STREX_PASSED           = 0x63,
    /*!< Counts the number of STREX instructions architecturally executed 
         and passed.                                                  Precise */

    PMU_EID_K_STREX_FAILED          = 0x64,
    /*!< Counts the number of STREX instructions architecturally executed 
         and failed.                                                  Precise */

    PMU_EID_K_DATA_EVICTION         = 0x65,
    /*!< Counts the number of eviction requests because of a linefill in 
        the data cache.                                               Precise */

    PMU_EID_K_NO_ISSUE              = 0x66, 
    /*! Counts the number of cycles where the issue stage does not dispatch
        any instruction because it is empty or cannot dispatch any 
        instructions.                                                Precise */

    PMU_EID_K_NO_ISSUE_EMPTY       = 0x67,
    /*!< Counts the number of cycles where the issue stage is empty. Precise */


    PMU_EID_K_RENAME_INSTRUCTIONS  = 0x68,
    /*!< Counts the number of instructions going through the Register 
         Renaming stage. This number is an approximate number of the total
         number of instructions speculatively executed, and even more
         approximate of the total number of instructions architecturally 
         executed. The approximation depends mainly on the branch 
         misprediction rate. The renaming stage can handle two instructions 
         in the same cycle so the event is two bits long:
            - b00 no instructions coming out of the core renaming stage
            - b01 one instruction coming out of the core renaming stage
            - b10 two instructions coming out of the core renaming stage.

        See Table A.17 for a description of how these values map to the
        PMUEVENT bus bits.                                        Approximate */

    PMU_EID_K_RSVD_0x69                    = 0x69,
    PMU_EID_K_RSVD_0x6A                    = 0x6a,
    PMU_EID_K_RSVD_0x6B                    = 0x6b,
    PMU_EID_K_RSVD_0x6C                    = 0x6c,
    PMU_EID_K_RSVD_0x6D                    = 0x6d,
    
    PMU_EID_K_PREDICTABLE_FUNCTION_RETURNS = 0x6e,
    /*! Counts the number of procedure returns whose condition codes do not
        fail, excluding all returns from exception. This count includes
        procedure returns which are flushed because of a previous load/store
        which aborts late.

        Only the following instructions are reported:
           - BX R14
           - MOV PC LR
           - POP {..,pc}
           - LDR pc,[sp],#offset.

       The following instructions are not reported:
          - LDMIA R9!,{..,PC} (ThumbEE state only)
          - LDR PC,[R9],#offset (ThumbEE state only)
          - BX R0 (Rm != R14)
          - MOV PC,R0 (Rm != R14)
          - LDM SP,{...,PC} (writeback not specified)
          - LDR PC,[SP,#offset] (wrong addressing mode).
                                                                  Approximate */

    PMU_EID_K_RSVD_0x6E             = 0x6e,
    PMU_EID_K_RSVD_0x6F             = 0x6f,
   /* ---------------------------------------------------------------------- */



    /* ---------------------------------------------------------------------- */
    /* 0x70 - 0x7F                                                            */
    /* ---------------------------------------------------------------------- */
    PMU_EID_K_INSTRUCTIONS_MAIN          = 0x70,
    /*!< Counts the number of instructions being executed in the main 
         execution pipeline of the processor, the multiply pipeline and
         arithmetic logic unit pipeline. The counted instructions are still
         speculative.                                            Approximate */

    PMU_EID_K_INSTRUCTIONS_SECOND       = 0x71,
    /*!< Counts the number of instructions being executed in the processor
         second execution pipeline (ALU). The counted instructions are still
         speculative.                                            Approximate */

    PMU_EID_K_INSTRUCTIONS_LOAD_STORE  = 0x72,
    /*!< Counts the number of instructions being executed in the Load/Store
         unit. The counted instructions are still speculative.   Approximate */

    PMU_EID_K_INSTRUCTIONS_FLOAT       = 0x73,
    /*! Counts the number of Floating-point instructions going through the
        Register Rename stage. Instructions are still speculative in this
        stage. 

        Two floating-point instructions can be renamed in the same cycle so
        the event is two bits long:
            - 0b00 no floating-point instruction renamed
            - 0b01 one floating-point instruction renamed
            - 0b10 two floating-point instructions renamed.

       See Table A.17 for a description of how these values map to the
       PMUEVENT bus bits.                                        Approximate */

    PMU_EID_K_INSTRUCTIONS_NEON       = 0x74,
    /*!< Counts the number of NEON instructions going through the Register
         Rename stage. Instructions are still speculative in this stage.

         Two NEON instructions can be renamed in the same cycle so the event 
         is two bits long:
            - 0b00 no NEON instruction renamed
            - 0b01 one NEON instruction renamed
            - 0b10 two NEON instructions renamed.
        See Table A.17 for a description of how these values map to the 
        PMUEVENT bus bits.                                       Approximate */

    PMU_EID_K_RSVD_0x75             = 0x75,
    PMU_EID_K_RSVD_0x76             = 0x76,
    PMU_EID_K_RSVD_0x77             = 0x77,
    PMU_EID_K_RSVD_0x78             = 0x78,
    PMU_EID_K_RSVD_0x79             = 0x79,
    PMU_EID_K_RSVD_0x7A             = 0x7a,
    PMU_EID_K_RSVD_0x7B             = 0x7b,
    PMU_EID_K_RSVD_0x7C             = 0x7c,
    PMU_EID_K_RSVD_0x7D             = 0x7d,
    PMU_EID_K_RSVD_0x7E             = 0x7e,
    PMU_EID_K_RSVD_0x7F             = 0x7f,
    /* ---------------------------------------------------------------------- */



    /* ---------------------------------------------------------------------- */
    /* 0x80 - 0x8F                                                            */
    /* ---------------------------------------------------------------------- */
    PMU_EID_K_STALLS_PLD                     = 0x80,
    /*!< Counts the number of cycles where the processor is stalled because 
         PLD slots are all full.                                  Approximate */

    PMU_EID_K_STALLS_WRITES                  = 0x81,
    /*!< Counts the number of cycles when the processor is stalled and the
         data side is stalled too because it is full and executing writes to
         the external memory.                                     Approximate */

    PMU_EID_K_STALLS_TLB_INSTRUCTION         = 0x82,
    /*!< Counts the number of stall cycles because of main TLB misses on
         requests issued by the instruction side.                 Approximate */

    PMU_EID_K_STALLS_TLB_DATA                = 0x83,
    /*!<  Counts the number of stall cycles because of main TLB misses on
          requests issued by the data side.                       Approximate */


    PMU_EID_K_STALLS_MICRO_TLB_INSTRUCTION  = 0x84,
    /*!< Counts the number of stall cycles because of micro TLB misses on the 
         instruction side. This event does not include main TLB miss stall
         cycles that are already counted in the corresponding main TLB event.
                                                                  Approximate */

    PMU_EID_K_STALLS_MICRO_TLB_DATA        = 0x85,
    /*!< Counts the number of stall cycles because of micro TLB misses on the
         data side. This event does not include main TLB miss stall cycles
         that are already counted in the corresponding main TLB event.
                                                                  Approximate */

    PMU_EID_K_STALLS_DMB                  = 0x86,
    /*!< Counts the number of stall cycles because of the execution of a DMB
         memory barrier. This includes all DMB instructions being executed, 
         even speculatively.                                      Approximate */

    PMU_EID_K_RSVD_0x87                  = 0x87,
    PMU_EID_K_RSVD_0x88                  = 0x88,
    PMU_EID_K_RSVD_0x89                  = 0x89,

    PMU_EID_K_CLOCK_ENABLED_INTEGER      = 0x8a,
    /*!< Counts the number of cycles during which the integer core clock is
         enabled.                                                 Approximate */

    PMU_EID_K_CLOCK_ENABLED_DATA         = 0x8B,
    /*!< Counts the number of cycles during which the Data Engine clock is 
         enabled.                                                Approximate  */
    /* ---------------------------------------------------------------------- */



    /* ---------------------------------------------------------------------- */
    /* 0x90 - 0x9F                                                            */
    /* ---------------------------------------------------------------------- */
    PMU_EID_K_INSTRUCTIONS_ISB           = 0x90,
    /*!< Counts the number of ISB instructions architecturally executed.
                                                                 Approximate  */

    PMU_EID_K_INSTRUCTIONS_DSB           = 0x91,
    /*!< Counts the number of DSB instructions architecturally executed.
                                                                 Approximate  */

    PMU_EID_K_INSTRUCTIONS_DMB           = 0x92,
    /*!< Counts the number of DMB instructions architecturally executed.
                                                                 Approximate  */

    PMU_EID_K_INTERRUPTS_EXTERNAL        = 0x93,
    /* Counts the number of external interrupts executed by the processor.
                                                                 Approximate  */

    PMU_EID_K_RSVD_0x94                  = 0x94,
    PMU_EID_K_RSVD_0x95                  = 0x95,
    PMU_EID_K_RSVD_0x96                  = 0x96,
    PMU_EID_K_RSVD_0x97                  = 0x97,
    PMU_EID_K_RSVD_0x98                  = 0x98,
    PMU_EID_K_RSVD_0x99                  = 0x99,
    PMU_EID_K_RSVD_0x9A                  = 0x9a,
    PMU_EID_K_RSVD_0x9B                  = 0x9b,
    PMU_EID_K_RSVD_0x9C                  = 0x9c,
    PMU_EID_K_RSVD_0x9D                  = 0x9d,
    PMU_EID_K_RSVD_0x9E                  = 0x9e,
    PMU_EID_K_RSVD_0x9F                  = 0x9f,
    /* ---------------------------------------------------------------------- */



    /* ---------------------------------------------------------------------- */
    /* 0xA0 - 0xAF                                                            */
    /* ---------------------------------------------------------------------- */
    PMU_EID_K_PLE_CACHE_REQUEST_COMPLETED = 0xa0,
    /*!< PLE cache line request completed                             Precise */

    PMU_EID_K_PLE_CACHE_REQUEST_SKIP     = 0xa1,
    /*!< PLE cache line request skipped                               Precise */

    PMU_EID_K_PLE_FIFO_FLUSH             = 0xa2,
    /*!< PLE FIFO flush                                               Precise */

    PMU_EID_K_PLE_REQUEST_DONE           = 0xa3,
    /*!< PLE request completed                                        Precise */

    PMU_EID_K_PLE_FIFO_OVERFLOW          = 0xa4,
    /*!< PLE FIFO overflow                                            Precise */

    PMU_EID_K_PLE_REQUEST_PROGRAMMED     = 0xa5,
    /*!< PLE request programmed                                       Precise */

    PMU_EID_K_RSVD_0xA6                  = 0xa6,
    PMU_EID_K_RSVD_0xA7                  = 0xa7,
    PMU_EID_K_RSVD_0xA8                  = 0xa8,
    PMU_EID_K_RSVD_0xA9                  = 0xa9,
    PMU_EID_K_RSVD_0xAA                  = 0xaa,
    PMU_EID_K_RSVD_0xAB                  = 0xab,
    PMU_EID_K_RSVD_0xAC                  = 0xac,
    PMU_EID_K_RSVD_0xAD                  = 0xad,
    PMU_EID_K_RSVD_0xAE                  = 0xae,
    PMU_EID_K_RSVD_0xAF                  = 0xaf,
    /* ---------------------------------------------------------------------- */

};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_EID_K_TD
#define       PMU_EID_K_TD
typedef enum _PMU_EID_K PMU_EID_K;
#endif
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif

#endif

