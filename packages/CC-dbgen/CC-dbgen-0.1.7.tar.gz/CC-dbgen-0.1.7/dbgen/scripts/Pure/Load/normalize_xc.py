
def normalize_xc(xc : str) -> str:
    """
    Normalize the notation for xc
    """


    if xc.lower() == 'pbe':
        return 'PBE'
    elif xc.lower() in ['beef','beef-vdw']:
        return 'BEEF'
    elif xc.lower() == 'rpbe':
        return 'RPBE'
    elif xc.lower() == 'mbeef':
        return 'mBEEF'
    elif xc.lower() == 'hse':
        return 'HSE'
    elif xc.lower() == 'lda':
        return 'LDA'
    else:
        raise ValueError("weird xc: ",xc)
