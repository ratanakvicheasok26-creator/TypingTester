package com.typingtogether.controller;

import com.typingtogether.dto.ApiResponse;
import com.typingtogether.dto.RecordRequest;
import com.typingtogether.exception.ResourceNotFoundException;
import com.typingtogether.model.User;
import com.typingtogether.service.AuthService;
import com.typingtogether.service.RecordService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class RecordController {

    private final AuthService authService;
    private final RecordService recordService;

    public RecordController(AuthService authService, RecordService recordService) {
        this.authService = authService;
        this.recordService = recordService;
    }

    private User resolveUser(String authorizationHeader) {
        if (authorizationHeader == null || !authorizationHeader.startsWith("Bearer ")) {
            throw new IllegalArgumentException("Authorization token is missing or invalid.");
        }
        String token = authorizationHeader.substring(7);
        return authService.validateToken(token)
                .orElseThrow(() -> new ResourceNotFoundException("Authenticated user not found."));
    }

    @GetMapping("/dashboard")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getDashboard(@RequestHeader("Authorization") String authorization) {
        User user = resolveUser(authorization);
        Map<String, Object> dashboard = recordService.getDashboardForUser(user);
        return ResponseEntity.ok(new ApiResponse<>(true, "Dashboard loaded.", dashboard));
    }

    @GetMapping("/records")
    public ResponseEntity<ApiResponse<Object>> getRecords(@RequestHeader("Authorization") String authorization) {
        User user = resolveUser(authorization);
        Map<String, Object> dashboard = recordService.getDashboardForUser(user);
        return ResponseEntity.ok(new ApiResponse<>(true, "Records loaded.", dashboard.get("records")));
    }

    @PostMapping("/records")
    public ResponseEntity<ApiResponse<Map<String, Object>>> createRecord(
            @RequestHeader("Authorization") String authorization,
            @Valid @RequestBody RecordRequest request) {
        User user = resolveUser(authorization);
        recordService.createRecord(user, request);
        Map<String, Object> dashboard = recordService.getDashboardForUser(user);
        return ResponseEntity.ok(new ApiResponse<>(true, "Record saved.", dashboard));
    }

    @PutMapping("/records/{id}")
    public ResponseEntity<ApiResponse<Map<String, Object>>> updateRecord(
            @RequestHeader("Authorization") String authorization,
            @PathVariable Long id,
            @Valid @RequestBody RecordRequest request) {
        User user = resolveUser(authorization);
        recordService.updateRecord(user, id, request);
        Map<String, Object> dashboard = recordService.getDashboardForUser(user);
        return ResponseEntity.ok(new ApiResponse<>(true, "Record updated.", dashboard));
    }

    @DeleteMapping("/records/{id}")
    public ResponseEntity<ApiResponse<Map<String, Object>>> deleteRecord(
            @RequestHeader("Authorization") String authorization,
            @PathVariable Long id) {
        User user = resolveUser(authorization);
        recordService.deleteRecord(user, id);
        Map<String, Object> dashboard = recordService.getDashboardForUser(user);
        return ResponseEntity.ok(new ApiResponse<>(true, "Record deleted.", dashboard));
    }
}
