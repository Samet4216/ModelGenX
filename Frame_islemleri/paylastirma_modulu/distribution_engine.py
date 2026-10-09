import os

def calculate_distribution(videos, annotators):
    """
    Ortak paylaştırma algoritması.
    Tüm modüller (Önizleme, Klasör Ağacı ve Worker) tarafından çağrılarak
    kod tekrarını engeller ve tutarlılık sağlar.
    """
    # 1. Toplam çıkartılacak kareyi hesapla
    total_extracted_all_videos = sum(
        (int(v.get("total_frames", 100)) // int(v.get("interval", 1))) 
        for v in videos
    )
    
    # 2. Aktif kişileri ve toplam ağırlığı belirle
    valid_annotators = [a for a in annotators if a.get("active", True)]
    total_weight = sum(a.get("weight", 1.0) for a in valid_annotators)
    
    # 3. Kotaları hesapla
    quotas = []
    for a in valid_annotators:
        quota = int(total_extracted_all_videos * (a.get('weight', 1.0) / total_weight))
        quotas.append({
            'person': a['name'],
            'role_filter': a.get('role', 'Tümü'),
            'target': quota,
            'current': 0
        })
        
    # Yuvarlama hatalarından kalan küsuratı son kişiye ekle
    if quotas:
        quotas[-1]['target'] += total_extracted_all_videos - sum(q['target'] for q in quotas)
        
    # 4. Dağıtımı Yap
    ui_assignments = []
    video_assignments = {}
    ann_idx = 0
    
    for vid in videos:
        vid_path = vid.get("path", "")
        v_name = os.path.splitext(vid.get("name", "Unknown"))[0]
        
        try: tf = int(vid.get("total_frames", 100))
        except: tf = 100
        try: iv = int(vid.get("interval", 1))
        except: iv = 1
            
        v_frames = tf // iv
        v_split = vid.get("split", "train")
        
        frames_left = v_frames
        current_start = 1
        vid_assign_list = []
        
        while frames_left > 0 and ann_idx < len(quotas):
            ann = quotas[ann_idx]
            
            if ann['role_filter'] not in ["Tümü", v_split]:
                ann_idx += 1
                continue
                
            space = ann['target'] - ann['current']
            if space <= 0:
                ann_idx += 1
                continue
                
            take = min(frames_left, space)
            
            ui_assignments.append({
                "person": ann['person'],
                "role": v_split,
                "video": v_name,
                "frames": take,
                "start": current_start
            })
            vid_assign_list.extend([ann['person']] * take)
            
            ann['current'] += take
            frames_left -= take
            current_start += take
            
            if ann['current'] >= ann['target']:
                ann_idx += 1
                
        # Eğer video bitmediyse, son geçerli kişiye geri kalanları ver (kurtarma)
        if frames_left > 0:
            for i in range(len(quotas)-1, -1, -1):
                if quotas[i]['role_filter'] in ["Tümü", v_split]:
                    take = frames_left
                    ui_assignments.append({
                        "person": quotas[i]['person'],
                        "role": v_split,
                        "video": v_name,
                        "frames": take,
                        "start": current_start
                    })
                    vid_assign_list.extend([quotas[i]['person']] * take)
                    quotas[i]['current'] += take
                    break
                    
        video_assignments[vid_path] = vid_assign_list
        
    return {
        "total_frames": total_extracted_all_videos,
        "valid_annotators": valid_annotators,
        "quotas": quotas,
        "ui_assignments": ui_assignments,
        "video_assignments": video_assignments
    }
