# --------------------------------------------------------
# Swin Transformer
# Copyright (c) 2021 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ze Liu
# --------------------------------------------------------

import os

import torch


def load_checkpoint(config, model, optimizer, lr_scheduler, logger):
    logger.info(f"==============> Resuming form {config.MODEL.RESUME}....................")
    if config.MODEL.RESUME.startswith("https"):
        checkpoint = torch.hub.load_state_dict_from_url(config.MODEL.RESUME, map_location="cpu", check_hash=True)
    else:
        checkpoint = torch.load(config.MODEL.RESUME, map_location="cpu")
    # msg = model.load_state_dict(checkpoint, strict=False)
    msg = model.load_state_dict(checkpoint["model"], strict=False)
    logger.info(msg)
    max_accuracy = 0.0
    if not config.EVAL_MODE and "optimizer" in checkpoint and "lr_scheduler" in checkpoint and "epoch" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer"])
        lr_scheduler.load_state_dict(checkpoint["lr_scheduler"])
        config.defrost()
        config.TRAIN.START_EPOCH = checkpoint["epoch"] + 1
        config.freeze()

        logger.info(f"=> loaded successfully '{config.MODEL.RESUME}' (epoch {checkpoint['epoch']})")
        if "max_accuracy" in checkpoint:
            max_accuracy = checkpoint["max_accuracy"]

    del checkpoint
    torch.cuda.empty_cache()
    return max_accuracy


def load_checkpoint_ft(pretrain_path, model, logger):
    logger.info(f"==============> Loading pretrained model form {pretrain_path}....................")
    state_dict = torch.load(pretrain_path, map_location="cpu")["state_dict_ema"]
    own_state_dict = model.state_dict()
    for name, param in state_dict.items():
        if name in own_state_dict and "head" not in name:
            own_state_dict[name].copy_(param)
    logger.info("=> loaded successfully")
    max_accuracy = 0.0
    del state_dict
    torch.cuda.empty_cache()
    return max_accuracy


def save_checkpoint_best(config, epoch, model, max_accuracy, optimizer, lr_scheduler, logger):
    save_state = {"model": model.state_dict(), "max_accuracy": max_accuracy, "epoch": epoch, "config": config}

    save_path = os.path.join(config.OUTPUT, "best_model.pth")
    logger.info(f"{save_path} saving......")
    torch.save(save_state, save_path)
    logger.info(f"{save_path} saved !!!")


def get_grad_norm(parameters, norm_type=2):
    if isinstance(parameters, torch.Tensor):
        parameters = [parameters]
    parameters = list(filter(lambda p: p.grad is not None, parameters))
    norm_type = float(norm_type)
    total_norm = 0
    for p in parameters:
        param_norm = p.grad.data.norm(norm_type)
        total_norm += param_norm.item() ** norm_type
    total_norm = total_norm ** (1.0 / norm_type)
    return total_norm


def auto_resume_helper(output_dir):
    checkpoints = os.listdir(output_dir)
    checkpoints = [ckpt for ckpt in checkpoints if ckpt.endswith("pth")]
    print(f"All checkpoints founded in {output_dir}: {checkpoints}")
    if len(checkpoints) > 0:
        latest_checkpoint = max([os.path.join(output_dir, d) for d in checkpoints], key=os.path.getmtime)
        print(f"The latest checkpoint founded: {latest_checkpoint}")
        resume_file = latest_checkpoint
    else:
        resume_file = None
    return resume_file
