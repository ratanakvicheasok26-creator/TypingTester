package com.typingtogether.service;

import com.typingtogether.dto.RecordRequest;
import com.typingtogether.exception.ResourceNotFoundException;
import com.typingtogether.model.TypingRecord;
import com.typingtogether.model.User;
import com.typingtogether.repository.TypingRecordRepository;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class RecordService {

    private final TypingRecordRepository recordRepository;

    public RecordService(TypingRecordRepository recordRepository) {
        this.recordRepository = recordRepository;
    }

    public List<TypingRecord> getRecordsForUser(User user) {
        return recordRepository.findAllByUserIdOrderByCreatedAtDesc(user.getId());
    }

    public TypingRecord createRecord(User user, RecordRequest request) {
        TypingRecord record = new TypingRecord(user, request.getTitle().trim(), request.getWpm(), request.getAccuracy(), request.getErrors(), request.getDuration(), request.getDifficulty().trim());
        return recordRepository.save(record);
    }

    public TypingRecord updateRecord(User user, Long id, RecordRequest request) {
        TypingRecord record = recordRepository.findById(id)
                .filter(existing -> existing.getUser().getId().equals(user.getId()))
                .orElseThrow(() -> new ResourceNotFoundException("Record not found or access denied."));

        record.setTitle(request.getTitle().trim());
        record.setWpm(request.getWpm());
        record.setAccuracy(request.getAccuracy());
        record.setErrors(request.getErrors());
        record.setDuration(request.getDuration());
        record.setDifficulty(request.getDifficulty().trim());

        return recordRepository.save(record);
    }

    public void deleteRecord(User user, Long id) {
        TypingRecord record = recordRepository.findById(id)
                .filter(existing -> existing.getUser().getId().equals(user.getId()))
                .orElseThrow(() -> new ResourceNotFoundException("Record not found or access denied."));
        recordRepository.delete(record);
    }

    public Map<String, Object> getDashboardForUser(User user) {
        List<TypingRecord> records = getRecordsForUser(user);

        double averageWpm = records.stream()
                .mapToInt(TypingRecord::getWpm)
                .average()
                .orElse(0.0);

        int bestWpm = records.stream()
                .mapToInt(TypingRecord::getWpm)
                .max()
                .orElse(0);

        Map<String, Object> summary = new HashMap<>();
        summary.put("username", user.getUsername());
        summary.put("email", user.getEmail());
        summary.put("totalRecords", records.size());
        summary.put("averageWpm", averageWpm);
        summary.put("bestWpm", bestWpm);
        summary.put("records", records.stream().map(record -> {
            Map<String, Object> payload = new HashMap<>();
            payload.put("id", record.getId());
            payload.put("title", record.getTitle());
            payload.put("wpm", record.getWpm());
            payload.put("accuracy", record.getAccuracy());
            payload.put("errors", record.getErrors());
            payload.put("duration", record.getDuration());
            payload.put("difficulty", record.getDifficulty());
            payload.put("createdAt", record.getCreatedAt().toString());
            return payload;
        }).collect(Collectors.toList()));

        return summary;
    }
}
