package com.typingtogether.model;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "typing_records")
public class TypingRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private int wpm;

    @Column(nullable = false)
    private int accuracy;

    @Column(nullable = false)
    private int errors;

    @Column(nullable = false)
    private int duration;

    @Column(nullable = false)
    private String difficulty;

    @Column(nullable = false)
    private Instant createdAt = Instant.now();

    public TypingRecord() {
    }

    public TypingRecord(User user, String title, int wpm, int accuracy, int errors, int duration, String difficulty) {
        this.user = user;
        this.title = title;
        this.wpm = wpm;
        this.accuracy = accuracy;
        this.errors = errors;
        this.duration = duration;
        this.difficulty = difficulty;
    }

    public Long getId() {
        return id;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public int getWpm() {
        return wpm;
    }

    public void setWpm(int wpm) {
        this.wpm = wpm;
    }

    public int getAccuracy() {
        return accuracy;
    }

    public void setAccuracy(int accuracy) {
        this.accuracy = accuracy;
    }

    public int getErrors() {
        return errors;
    }

    public void setErrors(int errors) {
        this.errors = errors;
    }

    public int getDuration() {
        return duration;
    }

    public void setDuration(int duration) {
        this.duration = duration;
    }

    public String getDifficulty() {
        return difficulty;
    }

    public void setDifficulty(String difficulty) {
        this.difficulty = difficulty;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
