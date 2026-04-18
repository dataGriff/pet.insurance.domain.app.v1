const request = require('supertest');
const { app, resetStore, createContributorToken, createViewerToken, seedItem } = require('./helpers');

beforeEach(() => resetStore());

describe('Contract Tests - Response Shapes', () => {
  describe('Auth endpoints', () => {
    it('POST /v1/auth/register returns 201 with AuthResponse shape', async () => {
      const res = await request(app)
        .post('/v1/auth/register')
        .send({ email: 'test@example.com', password: 'password123', firstName: 'Test', lastName: 'User', role: 'contributor' });
      expect(res.status).toBe(201);
      expect(res.body).toHaveProperty('accessToken');
      expect(res.body).toHaveProperty('refreshToken');
      expect(res.body).toHaveProperty('expiresIn');
      expect(res.body.user).toHaveProperty('id');
      expect(res.body.user).toHaveProperty('email');
      expect(res.body.user).toHaveProperty('firstName');
      expect(res.body.user).toHaveProperty('lastName');
      expect(res.body.user).toHaveProperty('role');
    });

    it('POST /v1/auth/login returns 200 with AuthResponse shape', async () => {
      await request(app).post('/v1/auth/register')
        .send({ email: 'test2@example.com', password: 'password123', firstName: 'T', lastName: 'U', role: 'viewer' });
      const res = await request(app).post('/v1/auth/login')
        .send({ email: 'test2@example.com', password: 'password123' });
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('accessToken');
      expect(res.body).toHaveProperty('refreshToken');
      expect(res.body).toHaveProperty('expiresIn');
      expect(res.body.user).toHaveProperty('id');
    });

    it('POST /v1/auth/logout returns 204', async () => {
      const { token } = await createContributorToken();
      const res = await request(app).post('/v1/auth/logout').set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(204);
    });

    it('POST /v1/auth/refresh returns 200 with AuthResponse shape', async () => {
      const regRes = await request(app).post('/v1/auth/register')
        .send({ email: 'refresh@example.com', password: 'password123', firstName: 'R', lastName: 'T', role: 'contributor' });
      const res = await request(app).post('/v1/auth/refresh')
        .send({ refreshToken: regRes.body.refreshToken });
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('accessToken');
      expect(res.body).toHaveProperty('refreshToken');
    });
  });

  describe('Item endpoints', () => {
    it('GET /v1/items returns 200 with ItemList shape', async () => {
      const { token } = await createContributorToken();
      const res = await request(app).get('/v1/items').set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('data');
      expect(res.body).toHaveProperty('pagination');
      expect(res.body.pagination).toHaveProperty('page');
      expect(res.body.pagination).toHaveProperty('pageSize');
      expect(res.body.pagination).toHaveProperty('total');
    });

    it('POST /v1/items returns 201 with Item shape', async () => {
      const { token } = await createContributorToken();
      const res = await request(app).post('/v1/items')
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'Shape Test Item' });
      expect(res.status).toBe(201);
      expect(res.body).toHaveProperty('id');
      expect(res.body).toHaveProperty('name', 'Shape Test Item');
      expect(res.body).toHaveProperty('description', null);
      expect(res.body).toHaveProperty('status', 'active');
      expect(res.body).toHaveProperty('contributorId');
      expect(res.body).toHaveProperty('createdAt');
      expect(res.body).toHaveProperty('updatedAt');
    });

    it('GET /v1/items/:itemId returns 200 with Item shape', async () => {
      const { token, user } = await createContributorToken();
      const item = seedItem(user.id);
      const res = await request(app).get(`/v1/items/${item.id}`).set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('id', item.id);
      expect(res.body).toHaveProperty('name');
      expect(res.body).toHaveProperty('status');
      expect(res.body).toHaveProperty('contributorId');
    });

    it('PATCH /v1/items/:itemId returns 200 with edited Item shape', async () => {
      const { token, user } = await createContributorToken();
      const item = seedItem(user.id);
      const res = await request(app).patch(`/v1/items/${item.id}`)
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'Patched Item', status: 'archived' });
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('name', 'Patched Item');
      expect(res.body).toHaveProperty('status', 'archived');
      expect(res.body).toHaveProperty('updatedAt');
    });

    it('DELETE /v1/items/:itemId returns 204', async () => {
      const { token, user } = await createContributorToken();
      const item = seedItem(user.id);
      const res = await request(app).delete(`/v1/items/${item.id}`)
        .set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(204);
    });
  });

  describe('Error responses', () => {
    it('returns 401 when no token provided', async () => {
      const res = await request(app).get('/v1/items');
      expect(res.status).toBe(401);
      expect(res.body).toHaveProperty('code');
      expect(res.body).toHaveProperty('message');
    });

    it('returns 403 when viewer accesses contributor-only endpoint', async () => {
      const { token } = await createViewerToken();
      const res = await request(app).post('/v1/items')
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'Forbidden Item' });
      expect(res.status).toBe(403);
      expect(res.body).toHaveProperty('code');
    });

    it('returns 404 for non-existent resource', async () => {
      const { token } = await createContributorToken();
      const res = await request(app)
        .get('/v1/items/00000000-0000-0000-0000-000000000000')
        .set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(404);
      expect(res.body).toHaveProperty('code', 'RESOURCE_NOT_FOUND');
    });

    it('returns 409 for duplicate email on register', async () => {
      await request(app).post('/v1/auth/register')
        .send({ email: 'dup@example.com', password: 'password123', firstName: 'D', lastName: 'U', role: 'contributor' });
      const res = await request(app).post('/v1/auth/register')
        .send({ email: 'dup@example.com', password: 'password123', firstName: 'D', lastName: 'U', role: 'contributor' });
      expect(res.status).toBe(409);
      expect(res.body).toHaveProperty('code', 'DUPLICATE_EMAIL');
    });
  });
});
