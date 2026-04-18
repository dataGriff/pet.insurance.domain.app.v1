const request = require('supertest');
const { app, resetStore } = require('./helpers');

beforeEach(() => resetStore());

describe('Auth routes', () => {
  describe('POST /v1/auth/register', () => {
    it('registers a new contributor and returns tokens', async () => {
      const res = await request(app).post('/v1/auth/register').send({
        email: 'contributor@example.com',
        password: 'password123',
        firstName: 'Alice',
        lastName: 'Smith',
        role: 'contributor',
      });
      expect(res.status).toBe(201);
      expect(res.body.accessToken).toBeDefined();
      expect(res.body.refreshToken).toBeDefined();
      expect(res.body.expiresIn).toBe(3600);
      expect(res.body.user.role).toBe('contributor');
    });

    it('registers a new viewer', async () => {
      const res = await request(app).post('/v1/auth/register').send({
        email: 'viewer@example.com',
        password: 'password123',
        firstName: 'Bob',
        lastName: 'Jones',
        role: 'viewer',
      });
      expect(res.status).toBe(201);
      expect(res.body.user.role).toBe('viewer');
    });

    it('returns 409 for duplicate email', async () => {
      await request(app).post('/v1/auth/register').send({
        email: 'dup@example.com', password: 'password123',
        firstName: 'A', lastName: 'B', role: 'contributor',
      });
      const res = await request(app).post('/v1/auth/register').send({
        email: 'dup@example.com', password: 'password123',
        firstName: 'A', lastName: 'B', role: 'contributor',
      });
      expect(res.status).toBe(409);
      expect(res.body.code).toBe('DUPLICATE_EMAIL');
    });
  });

  describe('POST /v1/auth/login', () => {
    it('logs in with correct credentials', async () => {
      await request(app).post('/v1/auth/register').send({
        email: 'login@example.com', password: 'mypassword',
        firstName: 'L', lastName: 'U', role: 'contributor',
      });
      const res = await request(app).post('/v1/auth/login').send({
        email: 'login@example.com', password: 'mypassword',
      });
      expect(res.status).toBe(200);
      expect(res.body.accessToken).toBeDefined();
    });

    it('returns 401 for wrong password', async () => {
      await request(app).post('/v1/auth/register').send({
        email: 'login2@example.com', password: 'correctpassword',
        firstName: 'L', lastName: 'U', role: 'contributor',
      });
      const res = await request(app).post('/v1/auth/login').send({
        email: 'login2@example.com', password: 'wrongpassword',
      });
      expect(res.status).toBe(401);
      expect(res.body.code).toBe('INVALID_CREDENTIALS');
    });

    it('returns 401 for non-existent email', async () => {
      const res = await request(app).post('/v1/auth/login').send({
        email: 'nobody@example.com', password: 'password',
      });
      expect(res.status).toBe(401);
    });
  });

  describe('POST /v1/auth/logout', () => {
    it('returns 204 with valid token', async () => {
      const reg = await request(app).post('/v1/auth/register').send({
        email: 'logout@example.com', password: 'password123',
        firstName: 'L', lastName: 'O', role: 'contributor',
      });
      const res = await request(app).post('/v1/auth/logout')
        .set('Authorization', `Bearer ${reg.body.accessToken}`);
      expect(res.status).toBe(204);
    });

    it('returns 401 without token', async () => {
      const res = await request(app).post('/v1/auth/logout');
      expect(res.status).toBe(401);
    });
  });

  describe('POST /v1/auth/refresh', () => {
    it('returns new tokens with valid refresh token', async () => {
      const reg = await request(app).post('/v1/auth/register').send({
        email: 'refresh@example.com', password: 'password123',
        firstName: 'R', lastName: 'F', role: 'contributor',
      });
      const res = await request(app).post('/v1/auth/refresh')
        .send({ refreshToken: reg.body.refreshToken });
      expect(res.status).toBe(200);
      expect(res.body.accessToken).toBeDefined();
      expect(res.body.refreshToken).toBeDefined();
    });

    it('returns 401 with invalid refresh token', async () => {
      const res = await request(app).post('/v1/auth/refresh')
        .send({ refreshToken: 'invalid-token' });
      expect(res.status).toBe(401);
    });
  });
});
