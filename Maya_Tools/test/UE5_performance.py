import unreal

# 1) 载入已存在的 Performance 资产（注意 .资产名）
perf = unreal.load_asset("/Game/CaptureManager/Imports/Mono_Video_Ingest/SLV_ev1051_000_001_000_1/CD_SLV_ev1051_000_001_000_1.CD_SLV_ev1051_000_001_000_1")



# 4) 开始处理并查看返回码
err = perf.start_pipeline()
print("StartPipelineError =", err)   # NONE 则成功
