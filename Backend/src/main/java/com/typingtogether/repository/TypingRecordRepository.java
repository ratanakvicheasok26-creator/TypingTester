package com.typingtogether.repository;

import com.typingtogether.model.TypingRecord;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface TypingRecordRepository extends JpaRepository<TypingRecord, Long> {
    List<TypingRecord> findAllByUserIdOrderByCreatedAtDesc(Long userId);
}
