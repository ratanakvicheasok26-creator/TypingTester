package com.typingtogether.service;

import com.typingtogether.dto.AuthResponse;
import com.typingtogether.dto.LoginRequest;
import com.typingtogether.dto.UserRequest;
import com.typingtogether.model.User;
import com.typingtogether.repository.UserRepository;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final TokenService tokenService;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    public AuthService(UserRepository userRepository, TokenService tokenService) {
        this.userRepository = userRepository;
        this.tokenService = tokenService;
    }

    public AuthResponse register(UserRequest request) {
        if (userRepository.findByEmail(request.getEmail()).isPresent()) {
            throw new IllegalArgumentException("Email is already registered.");
        }
        if (userRepository.findByUsername(request.getUsername()).isPresent()) {
            throw new IllegalArgumentException("Username is already taken.");
        }

        User user = new User(request.getUsername().trim(), request.getEmail().trim(), passwordEncoder.encode(request.getPassword()));
        userRepository.save(user);
        String token = tokenService.generateToken(user);
        return new AuthResponse(token, user.getUsername(), user.getEmail());
    }

    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new IllegalArgumentException("Invalid email or password."));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Invalid email or password.");
        }

        String token = tokenService.generateToken(user);
        return new AuthResponse(token, user.getUsername(), user.getEmail());
    }

    public Optional<User> validateToken(String token) {
        Long userId = tokenService.getUserIdFromToken(token);
        return userRepository.findById(userId);
    }
}
