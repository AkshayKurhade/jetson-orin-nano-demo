PROGRAM PassFailLogic
  VAR
    Jetson_Fail_Signal AT %MX0.0 : BOOL;
    Solenoid_Output AT %QX0.0 : BOOL;
  END_VAR

  VAR
    KickTimer : TP;
    KickDuration : TIME := T#500ms;
    ResetTrigger : BOOL;
  END_VAR

  
  KickTimer(IN := Jetson_Fail_Signal, PT := KickDuration);

 
  Solenoid_Output := KickTimer.Q;

  ResetTrigger := (NOT KickTimer.Q) AND Jetson_Fail_Signal;

  IF ResetTrigger THEN
      Jetson_Fail_Signal := FALSE;
  END_IF;
  
END_PROGRAM

CONFIGURATION Config0
  RESOURCE Res0 ON PLC
    TASK TaskMain(INTERVAL := T#50ms, PRIORITY := 0);
    PROGRAM Inst0 WITH TaskMain : PassFailLogic;
  END_RESOURCE
END_CONFIGURATION