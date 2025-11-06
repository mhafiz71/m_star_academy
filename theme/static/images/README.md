# Morning Star Academy Images

This directory contains images for the Morning Star Academy website.

## Current Images ✅

### School Photos
- `school-exterior.jpg` - Main school building exterior view
- `school-courtyard.jpg` - School courtyard with playground and swings
- `school-signage.jpg` - School sign with "Morning Star International School" logo
- `students-uniforms.jpg` - Students in their distinctive blue school uniforms
- `students-uniforms-2.jpg` - Additional photo of students in uniforms
- `classroom-interior.jpg` - Classroom environment

### Logo and Branding
- `logo.png` - School logo for navigation
- `logo-white.png` - White version of logo for dark backgrounds

## Image Usage in Templates

### Home Page (`templates/core/home.html`)
- Hero section: `school-exterior.jpg`
- Gallery: `school-exterior.jpg`, `students-uniforms.jpg`, `school-courtyard.jpg`

### Application Form (`templates/applications/apply.html`)
- Hero background: `school-signage.jpg`
- Hero side image: `students-uniforms.jpg`

### About Page (`templates/core/about.html`)
- Hero background: `school-exterior.jpg`
- School profile: `school-signage.jpg`
- Facilities: `classroom-interior.jpg`, `school-courtyard.jpg`, `school-exterior.jpg`
- Logo: `logo-white.png`

### Navigation (`templates/components/navigation.html`)
- Logo: `logo.png`

## Image Specifications
- Format: JPG for photos, PNG for logos
- All images are web-optimized and responsive
- Fallback systems implemented for graceful degradation
- Mobile-friendly display with proper aspect ratios